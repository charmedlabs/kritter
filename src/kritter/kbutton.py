#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import dash_devices
import dash_html_components as html
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import Kcomponent
from functools import wraps

class Kbutton(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kbutton', **kwargs)

        href = kwargs['href'] if 'href' in kwargs else None
        target = kwargs['target'] if 'target' in kwargs else None
        size = kwargs['size'] if 'size' in kwargs else "md"
        external_link = kwargs['external_link'] if 'external_link' in kwargs else None

        body = self.name if isinstance(self.name, list) else [self.name]
        button = dbc.Button(body,  disabled=self.disabled, href=href, target=target, external_link=external_link, size=size)

        self.set_layout(button, html.Div(button, style=self.col_style))

        if self.spinner:
            button.children.append(self.comp_spinner)

    def out_name(self, name):
        self.name = name
        if isinstance(name, list):
            children = name + [self.comp_spinner] if self.spinner else name
        else:
            children = [name, self.comp_spinner] if self.spinner else name
        return [Output(self.id, "children", children)]

    def out_url(self, url):
        return [Output(self.id, "href", url)]
    
    def out_click(self):
        return [Output(self.id, "n_clicks", -1)]

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, 'n_clicks')], state, self.service)
            def _func(*args):
                # Toss out n_clicks argument
                args = args[1:]
                return func(*args)
        return wrap_func

