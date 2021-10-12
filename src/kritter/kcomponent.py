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
        self.layout = kwargs['layout'] if 'layout' in kwargs else None
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.spinner = kwargs['spinner'] if 'spinner' in kwargs else False
        self.service = kwargs['service'] if 'service' in kwargs else dash_devices.Services.SHARED
        self.style = default_style.copy()
        self.disp = kwargs['disp'] if 'disp' in kwargs else True
        if 'style' in kwargs:
            self.style.update(kwargs['style']) 

        self.row_style = {"padding-top": str(self.style['vertical_padding'])+'px', "padding-bottom": str(self.style['vertical_padding'])+'px', 'max-width': str(self.style['max_width'])+'px', "margin": "0px"}
        self.col_style = {"padding-left": str(self.style['horizontal_padding'])+'px', "padding-right": str(self.style['horizontal_padding'])+'px'}

        self.id = kwargs['id'] if 'id' in kwargs else Kritter.new_id(label)
        self.id_div = self.id + '-div'
        self.id_col = self.id + '-col'
        self.id_row = self.id + '-row'
        self.id_label = self.id + '-label'
        self.label = dbc.Col(html.B(self.name), id=self.id_label, width=self.style['label_width'], className="text-right", style=self.col_style)

        if self.spinner:
            self.id_spinner = self.id + '-spinner'
            self.comp_spinner = html.Span(dbc.Spinner(color=self.style['color'], size='sm'), id=self.id_spinner, style={'display': 'none'})

    def set_layout(self, control, cols=None):
        self.control = control
        try:
            self.control.id = self.id
        except:
            pass
        self.cols = cols
        if self.cols is None:
            self.cols = [self.label, dbc.Col(self.control, width=self.style['control_width'], id=self.id_col, style=self.col_style)]
        self.row = dbc.Row(self.cols, align='center', justify='start', style=self.row_style, id=self.id_row)
        style = {'display': 'block'} if self.disp else {'display': 'none'}
        self.layout = html.Div([self.row], id=self.id_div, style=style)

    def append(self, component):
        from kritter import Kritter
        try:
            self.cols.append(component.cols)
        except AttributeError:
            self.cols = [self.cols, component.cols]
            self.row.children = self.cols
        if isinstance(component, Kcomponent):
            component.row_style["padding-top"] = component.row_style["padding-bottom"] = 0 # We will go with the vertical padding of the leftmost control.

    def out_spinner_disp(self, state, left_margin=5):
        if state:
            return [Output(self.id_spinner, 'style', {'display': 'inline', 'margin-left': f'{left_margin}px'})] + self.out_disabled(True)
        else:
            return [Output(self.id_spinner, 'style', {'display': 'none'})] + self.out_disabled(False) 

    def out_disp(self, state):
        if state:
            return [Output(self.id_div, 'style', {'display': 'block'})]
        else:
            return [Output(self.id_div, 'style', {'display': 'none'})]

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
    