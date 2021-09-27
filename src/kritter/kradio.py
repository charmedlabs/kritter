import dash_devices
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import Kcomponent

class Kradio(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kradio', **kwargs)

        options = kwargs['options'] if 'options' in kwargs else []
        value = kwargs['value'] if 'value' in kwargs else options[0] if len(options) else None
        options = [{'label': option, 'value': option} for option in options]

        radio = dbc.RadioItems(
            className="btn-group",
            labelClassName="btn btn-secondary",
            labelCheckedClassName="active",
            options=options,
            value=value,
        )
        
        cols = [self.label,
            dbc.Col(radio, width=self.style['control_width'], className="radio-group", id=self.id_col)]
        self.set_layout(radio, cols)

    def out_options(self, options):
        options = [{'label': option, 'value': option} for option in options]
        return [Output(self.id, "options", options)]


