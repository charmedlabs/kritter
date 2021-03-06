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
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import Kcomponent

class KtextBox(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('ktextbox', **kwargs)

        placeholder = kwargs['placeholder'] if 'placeholder' in kwargs else ""
        _type = kwargs['type'] if 'type' in kwargs else "text"
        min_length = kwargs['min_length'] if 'min_length' in kwargs else 0
        max_length = kwargs['max_length'] if 'max_length' in kwargs else -1
        value = kwargs['value'] if 'value' in kwargs else ""

        textbox = dbc.Input(placeholder=placeholder, type=_type, value=value, minLength=min_length, maxLength=max_length)
        self.set_layout(textbox)

    def out_type(self, _type):
        return [Output(self.id, "type", _type)]
