from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import Kcomponent

class Ktext(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('ktext', **kwargs)

        value = kwargs['value'] if 'value' in kwargs else ""

        self.set_layout(value)

    def out_value(self, value):
        return [Output(self.id_col, "children", value)]

    def state_value(self):
        return [State(self.id_col, "children")]



