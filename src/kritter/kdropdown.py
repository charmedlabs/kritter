#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import dash_html_components as html
import dash_devices
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from .kcomponent import Kcomponent


class Kdropdown(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('kdropdown', **kwargs)
        options = kwargs['options'] if 'options' in kwargs else []
        clearable = kwargs['clearable'] if 'clearable' in kwargs else False
        value = kwargs['value'] if 'value' in kwargs else options[0] if len(options) else None
        placeholder = kwargs['placeholder'] if 'placeholder' in kwargs else None
        options = [{'label': option, 'value': option} for option in options]

        dropdown = dcc.Dropdown(options=options, value=value, clearable=clearable, placeholder=placeholder)

        self.set_layout(dropdown)
        if self.spinner:
            self.row.children.append(self.comp_spinner)

    def out_spinner_disp(self, state):
        return super().out_spinner_disp(state, -5)

    def out_options(self, options):
        options = [{'label': option, 'value': option} for option in options]
        return [Output(self.id, "options", options)]


