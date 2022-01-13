from kritter import Kcomponent
from dash_devices import callback_context
from dash_devices.dependencies import Input, Output, ALL
import dash_bootstrap_components as dbc
import dash_html_components as html
from functools import wraps
import json

class KdropdownMenu(Kcomponent):

    def __init__(self, **kwargs):
        super().__init__('kdropdown', **kwargs)
        options = kwargs['options'] if 'options' in kwargs else []
        clearable = kwargs['clearable'] if 'clearable' in kwargs else False
        nav = kwargs['nav'] if 'nav' in kwargs else False
        value = kwargs['value'] if 'value' in kwargs else 0 if len(options) else None
        self.id_items = self.id + '-i'
        self.create_items(options)
        dropdown = dbc.DropdownMenu(label=self.name, children=self.items, disabled=self.disabled, style={"display": "inline-block"})
        if nav:
            dropdown.nav = True
            dropdown.in_navbar = True

        children = [dropdown, self.comp_spinner] if self.spinner else dropdown
        self.set_layout(dropdown, html.Div(children, style=self.col_style))

    def create_items(self, options):
        self.items = []
        for i, option in enumerate(options):
            id_ = {'type': self.id_items, 'index': i}
            if isinstance(option, dbc.DropdownMenuItem):
                option.id = id_
                self.items.append(option) 
            else:
                self.items.append(dbc.DropdownMenuItem(option, id=id_))

    def out_options(self, options):
        self.create_items(options)
        return [Output(self.id, "children", self.items)]
    
    # This won't work because we push_mods doesn't currently swork with pattern matching callbacks 
    #def out_option_disabled(self, index, disabled):
    #    return [Output(self.items[index].id, "disabled", disabled)]

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input({"type": self.id_items, 'index': ALL}, "n_clicks")], state, self.service)
            def _func(*args):
                index = json.loads(callback_context.triggered[0]['prop_id'].split('.')[0])['index']
                # Toss out n_clicks argument, add option to beginning
                args = [index] + list(args[1:])
                return func(*args)
        return wrap_func

