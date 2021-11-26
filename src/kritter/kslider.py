from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from .kcomponent import Kcomponent
from functools import wraps


class Kslider(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kslider', **kwargs)
        mxs = kwargs['mxs'] if 'mxs' in kwargs else (1, 100, 1)
        value = kwargs['value'] if 'value' in kwargs else mxs[0]
        updatemode = kwargs['updatemode'] if 'updatemode' in kwargs else "drag"

        self.format = kwargs['format'] if 'format' in kwargs else lambda val : f'{val}'
        self.id_val = self.id + '-text'

        slider = dcc.Slider(value=value, min=mxs[0], max=mxs[1], step=mxs[2], updatemode=updatemode, disabled=self.disabled, className="_nopadding")
        cols = [self.label,
            dbc.Col(slider, id=self.id_col, width=self.style['control_width']), 
            dbc.Col(self.format(value), id=self.id_val, width='auto', className="_nopadding"),
        ]
        self.set_layout(slider, cols)

        @self.kapp.callback(Output(self.id_val, 'children'),
            [Input(self.id, 'value')], (), self.service)
        def func(value):
            return self.format(value)

    def set_format(self, format_):
        self.format = format_  

    def out_min(self, value):
        return [Output(self.id, "min", value)]

    def out_max(self, value):
        return [Output(self.id, "max", value)]

    def out_step(self, value):
        return [Output(self.id, "step", value)]

