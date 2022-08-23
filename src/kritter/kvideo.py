#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os
import time
import numpy
import cv2
import base64
from .kstoremedia import KstoreMedia
from kritter.kvideocomp import KvideoComp
from .streamer import Streamer
from .kritter import file_in_path, MEDIA_DIR
from .kcomponent import Kcomponent
from dash_devices.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from functools import wraps
from .koverlay import Koverlay 

# Maximum encoding area.  Not all browsers can accept full HD video.  
# This keeps the encoding resolution reasonably low, but can be increased with 
# max_area parameter passed into Kvideo. 
MAX_AREA = 640*480
HIST_HEIGHT = 100


def make_divisible(val, d):
    # find closest integer that's divisible by d
    mod = val%d
    if mod < d/2:
        val -= mod
    else:
        val += d-mod
    return val 

class Kvideo(Kcomponent):

    def __init__(self, **kwargs): 
        super().__init__('kvideo', **kwargs)
        self.hist_disp = kwargs['hist_disp'] if 'hist_disp' in kwargs else False
        overlay = kwargs['overlay'] if 'overlay' in kwargs else False
        
        self.id_div = self.id + '-div'
        self.hist_graph_id = self.id + "-hist"
        self.hist_id = self.id + "-hist-cont"

        self.width = kwargs['width'] if 'width' in kwargs else None
        self.height = kwargs['height'] if 'height' in kwargs else None

        src = kwargs['src'] if 'src' in kwargs else None
        loop = kwargs['loop'] if 'loop' in kwargs else False
        controls = kwargs['controls'] if 'controls' in kwargs else True
        autoplay = kwargs['autoplay'] if 'autoplay' in kwargs else False

        self.video_style = kwargs['video_style'] if 'video_style' in kwargs else {}
        self.hist_style = kwargs['hist_style'] if 'hist_style' in kwargs else self.video_style
        self.max_area = kwargs['max_area'] if 'max_area' in kwargs else MAX_AREA
        self.hist_height = kwargs['hist_height'] if 'hist_height' in kwargs else HIST_HEIGHT
        self.source_width = self.source_height = None

        self.hist_update_period = kwargs['hist_update_period'] if 'hist_update_period' in kwargs else 0.25
        self.hist_update_time = 0
        self.streamer = Streamer(server=self.kapp.server, html=None, js=None)

        self.hist = html.Div(dcc.Graph(id=self.hist_graph_id, style=self._hist_style(), config={'displayModeBar': False}), id=self.hist_id, style={"display": "block" if self.hist_disp else "none"})
        if src is None:           
            self.video = KvideoComp(id=self.id, style=self._video_style())
        else:
            self.video = html.Video(id=self.id, src=self._build_src(src), controls=controls, muted=True, autoPlay=autoplay, loop=loop, style=self._video_style())

        if overlay:
            self.overlay = Koverlay(self.video, self.kapp, self.service)
            self.video.overlay_id = self.overlay.id
            self.layout = html.Div([self.overlay.layout, self.hist], id=self.id_div)
        else:
            self.overlay = None
            self.layout = html.Div([self.video, self.hist], id=self.id_div)

        # Create RGB histogram graph objects.
        zeros = numpy.zeros(64)
        self.hist_data = [
            go.Scatter(
                line=dict(color = "#0000ff"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 0, 255, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
                y = zeros
            ),
            go.Scatter(
                line=dict(color = "#00ff00"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(0, 255, 0, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
                y = zeros
            ),
            go.Scatter(
                line=dict(color = "#ff0000"),
                mode='lines',
                name='',
                fill='tozeroy',
                fillcolor="rgba(255, 0, 0, 0.25)",
                #hovertemplate='%{y:.1f}%',
                hoverinfo='none',
                y = zeros
            ),
        ]
        self.hist_figure = dict(
            data=self.hist_data, 
            layout=dict(
                yaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False),
                xaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False),
                showlegend=False,
                xpad=0,
                ypad=0,
                plot_bgcolor="black",
                margin=dict(l=0, b=0, t=0, r=0),  
            )
        )


    def _hist_style(self):
        style = {"padding": "0", "margin": "0", "width": "100%", "height": f"{self.hist_height}px"} 
        if self.width:
            style["max-width"] = f"{self.width}px"
        if self.hist_style:
            style.update(self.hist_style)
        return style       

    def _video_style(self):
        style = {"padding": "0", "margin": "0", "display": "block", "width": "100%", "height": "100%"}
        if self.width:
            style["max-width"] = f"{self.width}px"
        if self.height:
            style["max-height"] = f"{self.height}px"
        if self.video_style:
            style.update(self.video_style)
        return style

    def _calc_enc_resolution(self):
        if self.source_width*self.source_height>self.max_area:
            ar = self.source_width/self.source_height 
            self.enc_height = int((self.max_area/ar)**0.5)
            # Encoder needs width and height to be evenly divisible by 16.
            # This will find the closest values.
            self.enc_height = make_divisible(self.enc_height, 16)
            self.enc_width = int(self.enc_height * ar) 
            self.enc_width = make_divisible(self.enc_width, 16) 
        else:
            self.enc_width = self.source_width
            self.enc_height = self.source_height

    def _update_source_resolution(self, width, height):
        if self.source_width!=width or self.source_height!=height:
            self.source_width = width
            self.source_height = height
            # Take source_width/height and calc enc_width/height
            self._calc_enc_resolution()
            # Let video component know the source resolution so it can send the 
            # correct click coordinates.
            mods = [Output(self.id, "source_width", self.source_width), Output(self.id, "source_height", self.source_height)]
            # Update overlay domain, range to correspond to source resolution.
            if self.overlay is not None:
                mods += self.overlay.update_resolution(self.source_width, self.source_height)
            self.kapp.push_mods(mods)

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
            self.kapp.push_mods([Output(self.hist_graph_id, "figure", self.hist_figure)])
        except:
            pass

    def _build_src(self, src):
        if src is None:
            return ""
        elif isinstance(src, str):
            if src=="":
                return "" 
            # If the file is in our media_path, just add the MEDIA_DIR (we can load directly)
            if file_in_path(self.kapp.media_path, src):
                return os.path.join("/"+MEDIA_DIR, src)
            # Otherwise the best way to send the image is to load it, encode it, and send as base64 string
            else: 
                encoded = base64.b64encode(open(src, 'rb').read())
                return f"data:video/mp4;charset=utf-8;base64,{encoded.decode('utf-8')}" 
        # If it's a kcamera streamer, encode it as mp4, then and send as base64 string
        elif str(type(src))=="<class 'kcamera.streamer'>": # extension doesn't have accessible types
            sm = KstoreMedia()
            sm.store_video_stream(src)
            with open(sm.tempvideo, 'rb') as f:
                image = f.read()
            image = base64.b64encode(image)
            return f"data:video/mp4;charset=utf-8;base64,{image.decode('utf-8')}" 
        else:
            raise RuntimeError("Unsupported image type")

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

    def push_frame(self, frame, frameperiod=0, format="BGR24"):
        if frame is None: # kcamera can return None if it can't allocate memory
            return
        # No sense in sending updates to clients if there are none. 
        # (And in fact, it will block if there are no clients.)
        if self.kapp.clients:
            # If we get a tuple, assume that it's a (frame, timestamp, index) tuple
            # and toss the timestamp and index.
            if isinstance(frame, tuple):
                frame = frame[0]
            self._update_source_resolution(frame.shape[1], frame.shape[0])
            if frame.shape[0]!=self.enc_height or frame.shape[1]!=self.enc_width:
                frame = cv2.resize(frame, (self.enc_width, self.enc_height))
            self.streamer.push_frame(frame, frameperiod)
            if self.hist_disp:
                t = time.time()
                # The update rate is intended to be lower than the framerate.
                # It takes about 10ms to create the complete histogram on a
                # Raspberry Pi 4.  So 4Hz or 250ms is about 4% of a CPU core.
                if t - self.hist_update_time > self.hist_update_period:
                    self._update_histogram(frame)
                    self.hist_update_time = t

    def out_hist_enable(self, value):
        self.hist_disp = value
        return [Output(self.hist_id, 'style', {"display": "block" if value else "none"})]

    def out_width_height(self, width=False, height=False):
        if width!=False: # you can set width to None
            self.width = width
        if height!=False: # you can set height to None
            self.height = height
        style = self._video_style()
        mods = [Output(self.id, "style", style), Output(self.hist_graph_id, "style", self._hist_style())]
        if self.overlay is not None:
            mods += self.overlay.out_style(style)
        return mods

    def out_height(self, value):
        return self.out_width_height(height=value)

    def out_width(self, value):
        return self.out_width_height(width=value)

    def out_src(self, src):
        return [Output(self.id, "src", self._build_src(src))]

    def out_disp(self, state):
        style = {'display': 'block'} if state else {'display': 'none'}
        return [Output(self.id_div, "style", style)]
