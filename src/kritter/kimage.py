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
from dash_devices.dependencies import Input, Output
import dash_html_components as html
from kritter import Kcomponent, Koverlay, file_in_path, MEDIA_DIR
import base64
import cv2
import numpy as np

class Kimage(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('Kimage', **kwargs)

        self.id_div = self.id + '-div'
        # outer Div style
        # Even though Kcomponent has it's own styling, we're going with the strict CSS
        # styling because we're being displayed as a single column (no label, etc.)
        self.style = kwargs['style'] if 'style' in kwargs else {}
        src = kwargs['src'] if 'src' in kwargs else ""
        width = kwargs['width'] if 'width' in kwargs else None
        height = kwargs['height'] if 'height' in kwargs else None
        overlay = kwargs['overlay'] if 'overlay' in kwargs else False

        # Img style
        style = {"width": "100%", "height": "100%"}
        if width:
            style["max-width"] = f"{width}px"
        if height:
            style["max-height"] = f"{height}px"
        image = html.Img(id=self.id, src=self._build_src(src), style=style)

        if overlay:
            self.overlay = Koverlay(image, self.kapp, self.service)
            image = self.overlay.layout
        self.layout = html.Div(image, id=self.id_div, style=self.style)

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
                ext = src.lower().split('.')[-1]
                if ext=='gif' or ext=='png':
                    image_type = ext
                else:
                    image_type = 'jpeg'
                return f"data:image/{image_type};charset=utf-8;base64,{encoded.decode('utf-8')}" 
        # If it's an array, encode it as jpg, then and send as base64 string
        elif isinstance(src, np.ndarray):
            image = cv2.imencode('.jpg', src)[1].tobytes()
            image = base64.b64encode(image)
            return f"data:image/jpeg;charset=utf-8;base64,{image.decode('utf-8')}" 
        else:
            raise RuntimeError("Unsupported image type")

    def out_src(self, src):
        return [Output(self.id, "src", self._build_src(src))]

    def out_disp(self, state):
        style = {**self.style, 'display': 'block'} if state else {'display': 'none'}
        return [Output(self.id_div, "style", style)]
