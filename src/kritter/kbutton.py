import dash_devices
import dash_html_components as html
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import Kcomponent
from functools import wraps

class Kbutton(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kbutton', **kwargs)

        disabled = kwargs['disabled'] if 'disabled' in kwargs else False
        href = kwargs['href'] if 'href' in kwargs else None
        target = kwargs['target'] if 'target' in kwargs else None
        external_link = kwargs['external_link'] if 'external_link' in kwargs else None

        body = self.name if isinstance(self.name, list) else [self.name]
        button = dbc.Button(body,  disabled=disabled, href=href, target=target, external_link=external_link)

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

