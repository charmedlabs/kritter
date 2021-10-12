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

        button = dbc.Button([self.name],  disabled=disabled)

        self.set_layout(button, html.Div(button, style=self.col_style))

        if self.spinner:
            button.children.append(self.comp_spinner)

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

