#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import time
from dash_devices import Services
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from .kcomponent import Kcomponent
from functools import wraps

UPDATE_RATE = 10 #(updates/sec)

class Kslider(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kslider', **kwargs)
        mxs = kwargs['mxs'] if 'mxs' in kwargs else (1, 100, 1)
        value = kwargs['value'] if 'value' in kwargs else mxs[0]
        self.updatemode = kwargs['updatemode'] if 'updatemode' in kwargs else "drag"
        self.updatetext = kwargs['updatetext'] if 'updatetext' in kwargs else True
        self.range_ = kwargs['range'] if 'range' in kwargs else False
        updaterate = kwargs['updaterate'] if 'updaterate' in kwargs else UPDATE_RATE
        self.updateperiod = 0 if updaterate==0 else 1/updaterate
        # Use SHARED_MOST_RECENT because we're a slider and only the most recent values are needed
        self.service = kwargs['service'] if 'service' in kwargs else Services.SHARED_MOST_RECENT

        if 'format' in kwargs:
            self.format = kwargs['format'] 
        else:
            if self.updatetext: 
                if self.range_:
                    self.format = lambda val : f'{val[0]}'
                else:
                    self.format = lambda val : f'{val}'
            else:
                self.format = lambda val : ''
        self.id_text = self.id + '-text'

        component = dcc.RangeSlider if self.range_ else dcc.Slider
        slider = component(value=value, min=mxs[0], max=mxs[1], step=mxs[2], updatemode=self.updatemode, disabled=self.disabled, className="_nopadding")
        cols = [self.label,
            dbc.Col(slider, id=self.id_col, width=self.style['control_width']), 
            dbc.Col(self.format(value), id=self.id_text, width='auto', className="_nopadding"),
        ]
        self.set_layout(slider, cols)

        if self.updatetext:
            @self.kapp.callback(Output(self.id_text, 'children'),
                [Input(self.id, 'value')], (), self.service)
            def func(value):
                # Limiting update rate keeps things from being queued up in the browser
                if self.updatemode=="drag":
                    time.sleep(self.updateperiod)
                return self.format(value)

    def callback(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, 'value')], state, self.service)
            def _func(*args):
                result = func(*args)
                # Limiting update rate keeps things from being queued up in the browser,
                # but call the callback first to reduce latency. 
                if self.updatemode=="drag":
                    time.sleep(self.updateperiod)
                return result
        return wrap_func

    def set_format(self, format_):
        self.format = format_  

    def out_min(self, value):
        return [Output(self.id, "min", value)]

    def out_max(self, value):
        return [Output(self.id, "max", value)]

    def out_step(self, value):
        return [Output(self.id, "step", value)]

    def out_text(self, text):
        return [Output(self.id_text, "children", text)]
