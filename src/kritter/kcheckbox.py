from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from .kcomponent import Kcomponent
from functools import wraps


class Kcheckbox(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kcheckbox', **kwargs)

        value = kwargs['value'] if 'value' in kwargs else False
        value = ['True'] if value else []

        checkbox = dcc.Checklist(options=[{'label': '', 'value': 'True'}], value=value)
        self.set_layout(checkbox)
        if self.spinner:
            self.row.children.append(self.comp_spinner)

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, 'value')], state, self.service)
            def _func(*args):
                args = list(args)
                args[0] = bool(args[0]) # Convert to proper boolean values
                return func(*args)
        return wrap_func

    def out_value(self, value):
        return [Output(self.id, "value", ['True'] if value else [])]
