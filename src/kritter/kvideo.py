import time
import numpy
import cv2
from kritter.kvideocomp import KvideoComp
from .streamer import Streamer
from .kcomponent import Kcomponent
from dash_devices.dependencies import Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go


class Kvideo(Kcomponent):

    def __init__(self, **kwargs): 
        super().__init__('kvideo', **kwargs)
        hist_disp = kwargs['hist_disp'] if 'hist_disp' in kwargs else False
        
        self.id_div = self.id + '-div'
        self.hist_graph_id = self.id + "-hist"
        self.hist_id = self.id + "-hist-cont"

        self.width = kwargs['width'] if 'width' in kwargs else 640
        self.height = kwargs['height'] if 'height' in kwargs else 480
        self.hist_update_period = kwargs['hist_update_period'] if 'hist_update_period' in kwargs else 0.25
        self.hist_update_time = 0
        self.streamer = Streamer(server=self.kapp.server, html=None, js=None)

        self.hist = dbc.Collapse(
            dcc.Graph(id=self.hist_graph_id, style={"padding": "0px", "margin": "0px"}, config={'displayModeBar': False}), 
            is_open=hist_disp, id=self.hist_id, style={"margin": str(-self.style['vertical_padding']-2)+"px 0px "+str(self.style['vertical_padding']+1)+"px 0px"}
        )
        self.video = KvideoComp(id=self.id, width=self.width, height=self.height)
        self.layout = html.Div([self.video, self.hist], id=self.id_div)

        # Create RGB histogram graph objects.
        self.hist_data = [
            go.Scatter(
                line=dict(color = "#0000ff"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 0, 255, 0.25)",
                hovertemplate='%{y:.1f}%'
                #hoverinfo='none',
            ),
            go.Scatter(
                line=dict(color = "#00ff00"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 255, 0, 0.25)",
                hovertemplate='%{y:.1f}%'
                #hoverinfo='none',
            ),
            go.Scatter(
                line=dict(color = "#ff0000"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(255, 0, 0, 0.25)",
                hovertemplate='%{y:.1f}%'
                #hoverinfo='none',
            ),
        ]
        self.hist_figure = dict(
            data=self.hist_data, 
            layout=dict(
                yaxis=dict(zeroline=False, showticklabels=False, fixedrange=True),
                xaxis=dict(zeroline=False, showticklabels=False, fixedrange=True),
                showlegend=False,
                width=self.width, 
                height=100, 
                xpad=0,
                ypad=0,
                plot_bgcolor="black",
                margin=dict(l=0, b=0, t=0, r=0),  
            )
        )

    def _update_histogram(self, frame):
        # Create histograms for the 3 color channels, RGB.
        for i in range(3):
            color = frame[:, :, i]
            color = color.flatten()
            colorsub = color[::32]
            hist = numpy.histogram(colorsub, bins=64, range=(0, 255))[0]
            # Scale to reflect percentages.
            hist = hist/len(colorsub)*100
            self.hist_data[i].y = hist
        try:
            self.kapp.push_mods({
                self.hist_graph_id: {"figure": self.hist_figure}
            })
        except:
            pass

    def push_frame(self, frame, format="BGR24"):
        if frame is None: # kcamera can return None if it can't allocate memory
            return
        # No sense in sending updates to clients if there are none. 
        # (And in fact, it will block if there are no clients.)
        if self.kapp.clients:
            # If we get a tuple, assume that it's a (frame, timestamp, index) tuple
            # and toss the timestamp and index.
            if isinstance(frame, tuple):
                frame = frame[0]
            if frame.shape[0]!=self.height or frame.shape[1]!=self.width:
                frame = cv2.resize(frame, (self.width, self.height))
            self.streamer.push_frame(frame)
            if self.hist.is_open:
                # Update histogram width if needed
                self.hist_figure["layout"]["width"] = self.video.width
                t = time.time()
                # The update rate is intended to be lower than the framerate.
                # It takes about 10ms to create the complete histogram on a
                # Raspberry Pi 4.  So 4Hz or 250ms is about 4% of a CPU core.
                if t - self.hist_update_time > self.hist_update_period:
                    self._update_histogram(frame)
                    self.hist_update_time = t

    def out_hist_enable(self, value):
        return [Output(self.hist_id, 'is_open', value)]

    def out_height(self, value):
        return [Output(self.id, 'height', value)]

    def out_width(self, value):
        return [Output(self.id, 'width', value)]
