#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import dash_bootstrap_components as dbc
from dash_devices.dependencies import Input, Output
import dash_html_components as html
from kritter import Kritter, Kcomponent
from functools import wraps

HEIGHT = 150

class Kchecklist(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('Kchecklist', **kwargs)

        options = kwargs['options'] if 'options' in kwargs else []
        value = kwargs['value'] if 'value' in kwargs else [] 
        scrollable = kwargs['scrollable'] if 'scrollable' in kwargs else False
        clear_check_all = kwargs['clear_check_all'] if 'clear_check_all' in kwargs else False
        body = self.name if isinstance(self.name, list) else [self.name]

        button = dbc.Button(body, disabled=self.disabled)
        options = [{'label': option, 'value': option} for option in options]
        self.checklist = dbc.Checklist(options=options, value=value, id=self.kapp.new_id())
        if clear_check_all:
            check_all = html.Button(Kritter.icon("check-square", padding=0), id=self.kapp.new_id(), style={"margin": "2px 2px 2px 0", "border-width": "0"})
            clear_all = html.Button(Kritter.icon("square-o", padding=0), id=self.kapp.new_id(), style={"margin": "2px", "border-width": "0"})
            po_children = [
                html.Div([check_all, clear_all]),
                html.Div(self.checklist)]

            @self.kapp.callback(None, [Input(check_all.id, "n_clicks")], service=self.service)
            def func(val):
                value = [option['value'] for option in self.checklist.options]
                return Output(self.checklist.id, "value", value)

            @self.kapp.callback(None, [Input(clear_all.id, "n_clicks")], service=self.service)
            def func(val):
                return Output(self.checklist.id, "value", [])
        else:
            po_children = self.checklist

        if scrollable:
            style = {"padding": "5px", "height": f"{HEIGHT}px", "overflow-y": "auto"}
        else:
            style = {"padding": "5px"}
        po_body = html.Div(po_children, style=style)
        po = dbc.Popover(po_body, trigger="legacy", hide_arrow=True)
        self.set_layout(button, html.Div([button, po]))
        po.target = button.id

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.checklist.id, 'value')], state, self.service)
            def _func(*args):
                return func(*args)
        return wrap_func
