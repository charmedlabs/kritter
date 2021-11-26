from kritter import Kcomponent
from dash_devices import callback_context
from dash_devices.dependencies import Input, Output, ALL
import dash_bootstrap_components as dbc
import dash_html_components as html
from functools import wraps


class KdropdownMenu(Kcomponent):

    def __init__(self, **kwargs):
        super().__init__('kdropdown', **kwargs)
        self.options = kwargs['options'] if 'options' in kwargs else []
        clearable = kwargs['clearable'] if 'clearable' in kwargs else False
        value = kwargs['value'] if 'value' in kwargs else self.options[0] if len(self.options) else None
        options = [dbc.DropdownMenuItem(option, id={'type': "dd", 'index': i}) for i, option in enumerate(self.options)]

        dropdown = dbc.DropdownMenu(label=self.name, children=options)

        self.set_layout(dropdown, html.Div(dropdown, style=self.col_style))

    def out_options(self, options):
        self.options = options
        options = [dbc.DropdownMenuItem(option, id={'type': "dd", 'index': i}) for i, option in enumerate(self.options)]
        return [Output(self.id, "children", options)]


    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input({"type": "dd", 'index': ALL}, "n_clicks")], state, self.service)
            def _func(*args):
                index = json.loads(callback_context.triggered[0]['prop_id'].split('.')[0])['index']
                # Toss out n_clicks argument, add option to beginning
                args = [self.options[index]] + list(args[1:])
                return func(*args)
        return wrap_func

