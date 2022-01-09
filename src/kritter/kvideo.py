import time
import numpy
import cv2
from kritter.kvideocomp import KvideoComp
from .streamer import Streamer
from .kcomponent import Kcomponent
from dash_devices.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go
from functools import wraps


def _needs_overlay(func):
    @wraps(func)
    def wrap_func(self, *args, **kwargs):
        if self.overlay is None:
            raise RuntimeError("overlay needs to be enabled! (Use overlay=True when instantiating Kvideo.)")
        return func(self, *args, **kwargs)
    return wrap_func

class Kvideo(Kcomponent):

    def __init__(self, **kwargs): 
        super().__init__('kvideo', **kwargs)
        hist_disp = kwargs['hist_disp'] if 'hist_disp' in kwargs else False
        overlay = kwargs['overlay'] if 'overlay' in kwargs else False
        
        self.id_div = self.id + '-div'
        self.hist_graph_id = self.id + "-hist"
        self.hist_id = self.id + "-hist-cont"

        self.width = kwargs['width'] if 'width' in kwargs else 640
        self.height = kwargs['height'] if 'height' in kwargs else 480
        self.source_width = kwargs['source_width'] if 'source_width' in kwargs else self.width
        self.source_height = kwargs['source_height'] if 'source_height' in kwargs else self.height
        self.hist_update_period = kwargs['hist_update_period'] if 'hist_update_period' in kwargs else 0.25
        self.hist_update_time = 0
        self.streamer = Streamer(server=self.kapp.server, html=None, js=None)

        self.hist = dbc.Collapse(
            dcc.Graph(id=self.hist_graph_id, style={"padding": "0px", "margin": "0px"}, config={'displayModeBar': False}),
            is_open=hist_disp, id=self.hist_id, style={"margin": f"{-self.style['vertical_padding']-1}px 0px {self.style['vertical_padding']+1}px 0px"}
        )
 
        self.video = KvideoComp(id=self.id, width=self.width, height=self.height)
        if overlay:
            self.overlay_id = self.id + "-overlay"
            self.video.overlay_id = self.overlay_id
            self.overlay_shapes = []
            self.overlay_annotations = []
            self.overlay_figure = dict(
                layout=dict(
                    shapes=self.overlay_shapes,
                    annotations=self.overlay_annotations,
                    showlegend=False,
                    xpad=0,
                    ypad=0,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, b=0, t=0, r=0),  
                    yaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[self.source_height-1, 0]),
                    xaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[0, self.source_width-1])
                )
            )
            self._update_overlay_figure()
            self.overlay = dcc.Graph(id=self.overlay_id, figure=self.overlay_figure, config={'displayModeBar': False}, style={"padding": "0px", "margin": "0px", "position": "absolute", "top": "0px", "left": "0px"})
            vdiv = html.Div([self.video, self.overlay], style={"position": "relative"})
            self.layout = html.Div([vdiv, self.hist], id=self.id_div)
        else:
            self.overlay = None
            self.layout = html.Div([self.video, self.hist], id=self.id_div)

        # Create RGB histogram graph objects.
        self.hist_data = [
            go.Scatter(
                line=dict(color = "#0000ff"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 0, 255, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
            ),
            go.Scatter(
                line=dict(color = "#00ff00"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 255, 0, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
            ),
            go.Scatter(
                line=dict(color = "#ff0000"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(255, 0, 0, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
            ),
        ]
        self.hist_figure = dict(
            data=self.hist_data, 
            layout=dict(
                yaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False),
                xaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False),
                showlegend=False,
                width=self.width, 
                height=100, 
                xpad=0,
                ypad=0,
                plot_bgcolor="black",
                margin=dict(l=0, b=0, t=0, r=0),  
            )
        )


    def _update_overlay_figure(self):
        self.overlay_figure['layout']['width'] = self.width 
        self.overlay_figure['layout']['height'] = self.height 



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

    @_needs_overlay
    def callback_draw(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.overlay_id, "relayoutData")], state, self.service)
            def _func(*args):
                return func(*args)
        return wrap_func

    def callback_click(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, 'click_data')], state, self.service)
            def _func(*args):
                return func(*args)
        return wrap_func
 
    def send_keyframe(self):
        self.streamer.send_keyframe()

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
                t = time.time()
                # The update rate is intended to be lower than the framerate.
                # It takes about 10ms to create the complete histogram on a
                # Raspberry Pi 4.  So 4Hz or 250ms is about 4% of a CPU core.
                if t - self.hist_update_time > self.hist_update_period:
                    self._update_histogram(frame)
                    self.hist_update_time = t

    @_needs_overlay
    def draw_circle(self, x_center, y_center, radius, fillcolor="gray", line=None, editable=False):
        circle = dict(type="circle", xref="x", yref="y", x0=x_center-radius, x1=x_center+radius, y0=y_center-radius, y1=y_center+radius, fillcolor=fillcolor, editable=editable)
        if line:
            circle['line'] = line
        self.overlay_shapes.append(circle)

    @_needs_overlay
    def draw_line(self, x0, y0, x1, y1, line={}, editable=False):
        line__ = dict(color="gray", width=2)
        line__.update(line)
        line_ = dict(type="line", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1, line=line__, editable=editable)
        self.overlay_shapes.append(line_)

    @_needs_overlay
    def draw_rect(self, x0, y0, x1, y1, fillcolor="gray", line=None, editable=False):
        rect = dict(type="rect", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1, fillcolor=fillcolor, editable=editable)
        if line:
            rect['line'] = line
        self.overlay_shapes.append(rect)

    @_needs_overlay
    def draw_shape(self, points, fillcolor="gray", line=None, editable=False):
        try:
            for i, p in enumerate(points):
                if i==0:
                    path = "M "
                else:
                    path += " L "
                path += f"{p[0]} {p[1]}"
            path += " Z"
        except:
            raise RuntimeError(f"draw_shape() points in wrong format -- need to be [(x0, y0), (x1, y1), ...]. You passed: {points}")

        shape = dict(type="path", xref="x", yref="y", path=path, fillcolor=fillcolor, editable=editable)
        if line:
            shape['line'] = line
        self.overlay_shapes.append(shape)

    @_needs_overlay
    def draw_text(self, x0, y0, text, font={}, fillcolor="white", padding=2, xanchor="center", yanchor="center"):
        font_ = dict(family="sans serif", size=16, color="gray")
        font_.update(font)
        text_ = dict(text=text, x=x0, y=y0, xref="x", yref="y", font=font, showarrow=False, borderwidth=0, borderpad=padding, bgcolor=fillcolor, xanchor=xanchor, yanchor=yanchor)
        self.overlay_annotations.append(text_)

    # rect, line, circle, openpath, closedpath
    @_needs_overlay
    def draw_user(self, shape, fillcolor="gray", line=None):
        self.overlay_figure['layout']['dragmode'] = f"draw{shape}" 
        self.overlay_figure['layout']['newshape'] = dict(line=line, fillcolor=fillcolor)

    @_needs_overlay
    def draw_clear(self):
        self.overlay_shapes.clear()
        self.overlay_annotations.clear()

    @_needs_overlay
    def out_draw_overlay(self):
        return [Output(self.overlay_id, "figure", self.overlay_figure)]  

    def out_hist_enable(self, value):
        return [Output(self.hist_id, 'is_open', value)]

    def out_height(self, value):
        mods = []
        self.height = value
        if self.overlay is not None:
            self._update_overlay_figure()
            mods += self.out_draw_overlay()
        return mods + [Output(self.id, 'height', value)]

    def out_width(self, value):
        mods = []
        self.width = value
        self.hist_figure["layout"]["width"] = self.width
        if self.overlay is not None:
            self._update_overlay_figure()
            mods += self.out_draw_overlay()
        return mods + [Output(self.id, 'width', value)]
