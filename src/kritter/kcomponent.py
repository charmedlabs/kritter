#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from dash_devices.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_devices
import dash_html_components as html
from functools import wraps

default_style = dict(
    label_width=3,
    control_width=6,
    vertical_padding=5,
    horizontal_padding=5,
    max_width=640,
    color='#909090',
)

class Kcomponent:
    
    kcomponent_id_count = 0

    def __init__(self, label, **kwargs):
        from .kritter import Kritter
        self.kapp = kwargs['kapp'] if 'kapp' in kwargs else Kritter.kapp
        self.grid = kwargs['grid'] if 'grid' in kwargs else True
        self.layout = kwargs['layout'] if 'layout' in kwargs else None
        self.name = kwargs['name'] if 'name' in kwargs else ""
        self.spinner = kwargs['spinner'] if 'spinner' in kwargs else False
        self.service = kwargs['service'] if 'service' in kwargs else dash_devices.Services.SHARED
        self.disabled = kwargs['disabled'] if 'disabled' in kwargs else False
        self.disp = kwargs['disp'] if 'disp' in kwargs else True
        self.style = default_style.copy()
        if 'style' in kwargs:
            self.style.update(kwargs['style']) 

        self.row_style = {"padding": "0", "margin": "0", 'max-width': str(self.style['max_width'])+'px', }
        self.col_style = {"padding": f"{self.style['vertical_padding']}px {self.style['horizontal_padding']}px {self.style['vertical_padding']}px {self.style['horizontal_padding']}px"}

        self.id = kwargs['id'] if 'id' in kwargs else self.kapp.new_id(label)
        self.id_col = self.id + '-col'
        self.id_row = self.id + '-row'
        self.id_label = self.id + '-label'
        if self.grid:
            self.label = dbc.Col(html.B(self.name), id=self.id_label, width=self.style['label_width'], className="text-right", style=self.col_style)
        else:
            self.label = html.Div(html.B(self.name), id=self.id_label, style=self.col_style)

        if self.spinner:
            self.id_spinner = self.id + '-spinner'
            self.comp_spinner = html.Span(dbc.Spinner(color=self.style['color'], size='sm'), id=self.id_spinner, style={'display': 'none'})

    def set_layout(self, control, cols=None):
        self.control = control
        try:
            self.control.id = self.id
        except:
            self.id = self.id_col
        self.cols = cols
        if self.cols is None:
            if self.grid:
                self.cols = [self.label, dbc.Col(self.control, width=self.style['control_width'], id=self.id_col, style=self.col_style)]
            else:
                self.cols = [self.label, html.Div(self.control, id=self.id_col, style=self.col_style)]
        if not self.name and isinstance(self.cols, list) and len(self.cols)>=2:
            self.cols = self.cols[1:]

        self.layout = dbc.Row(self.cols, align='center', justify='start', style=self.row_style, id=self.id_row)

        # Make sure we can call out_disp on this component and set display to none
        # for each sub-component.
        cols = self.cols if isinstance(self.cols, list) else [self.cols]
        self.col_info = []
        for c in cols:
            if not hasattr(c, "id"):
                c.id = self.kapp.new_id()
            if "spinner" in c.id: # spinner is displayed independently of component
                continue
            if not hasattr(c, "style"):
                c.style = {}
            c.style.update({'display': 'block'} if self.disp else {'display': 'none'})
            self.col_info.append({"id": c.id, "style": c.style})

    def append(self, component):
        if not isinstance(component, Kcomponent):
            raise Exception("Cannot append components that are not Kcomponents.")
        scols = self.cols if isinstance(self.cols, list) else [self.cols]
        ccols = component.cols if isinstance(component.cols, list) else [component.cols]
        self.cols = scols + ccols
        self.layout.children = self.cols

    @property
    def value(self):
        return self.control.value

    def out_spinner_disp(self, state, left_margin=5, disable=None):
        if state:
            return [Output(self.id_spinner, 'style', {'display': 'inline', 'margin-left': f'{left_margin}px'})] + self.out_disabled(disable if disable is not None else True)
        else:
            return [Output(self.id_spinner, 'style', {'display': 'none'})] + self.out_disabled(disable if disable is not None else False) 

    def out_disp(self, state):
        mods = []
        for i in self.col_info:
            i['style'].update({'display': 'block'} if state else {'display': 'none'})
            mods += [Output(i['id'], 'style', i['style'])]
        return mods

    def out_disabled(self, disabled):
        return [Output(self.id, "disabled", disabled)]

    def out_value(self, value):
        return [Output(self.id, "value", value)]

    def state_value(self):
        return [State(self.id, "value")]

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, 'value')], state, self.service)
            def _func(*args):
                return func(*args)
        return wrap_func
    