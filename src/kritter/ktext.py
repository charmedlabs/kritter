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
from .kcomponent import Kcomponent

class Ktext(Kcomponent):
    def __init__(self, **kwargs):
        super().__init__('ktext', **kwargs)

        value = kwargs['value'] if 'value' in kwargs else ""

        self.set_layout(value)

    def out_value(self, value):
        return [Output(self.id, "children", value)]

    def state_value(self):
        return [State(self.id, "children")]



