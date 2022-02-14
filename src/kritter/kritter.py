#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from . import excepthook
from quart import send_file
from dash_devices import Dash, callback_context
from dash_devices.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from hypercorn.config import Config
from hypercorn.asyncio import serve
import urllib.parse
import os
import asyncio
import contextvars
import subprocess
import time
from .kcomponent import Kcomponent
from .util import file_in_path

MEDIA_DIR = "media"
MEDIA_URL_PATH = "/" + MEDIA_DIR
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PORT = 5000

KRITTER_STYLE = '''
.radio-group .custom-control-input ~ .custom-control-label::before {
  content: none;
}

.radio-group .custom-radio .custom-control-input ~ .custom-control-label::after {
  content: none;
}

/* restyle radio items */
.radio-group .custom-control {
  padding-left: 0;
}

.radio-group .btn-group > .custom-control:not(:last-child) > .btn {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.radio-group .btn-group > .custom-control:not(:first-child) > .btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  margin-left: -1px;
}

.VirtualizedSelectOption { 
  white-space: nowrap;  
}

._nopadding {
    padding: 0px !important;   
    margin: 0px !important; 
} 

._slider {
    padding: 5px 0 5px 0 !important;   
    margin: 0px !important; 
}
'''

def index_string(style):
    return '''
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Cache-control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {%metas%}
        <title>{%title%}</title>
        {%css%}
        <style>
        ''' + style + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def run_kterm(port, command="bash", shared=True, block=False, logfile=None):
    _command = ["python3", os.path.join(BASE_DIR, "kterm", "kterm.py"), "-p", str(port)]
    if command!="bash":
        _command.extend(["-c", command])
    if shared:
        _command.append("-s")
    if logfile:
        _command.extend(["-l", logfile])

    if block:
        return subprocess.run(_command)
    else:
        return subprocess.Popen(_command)

# There isn't a class property in python...
class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class Kritter(Dash):

    # Context variable for referencing the kapp variable.  
    # If we have more than one kritter server, we can either pass
    # around the different kapp objects, or we can create a new context
    # by calling Kritter.new_context(func) where func()  
    # can instantiate a new Kritter and references to Kritter.kapp will 
    # be independent from the other kritter servers.   
    _kapp_var = contextvars.ContextVar('kapp')

    @classproperty 
    def kapp(cls):
        try:
            return cls._kapp_var.get()
        except:
            return None 

    @classmethod
    def new_context(cls, func):
        context = contextvars.copy_context()
        context.run(func)

    # Used for id generator
    _id_count = 0

    def __init__(self, server=True):
        
        super().__init__("kritter", server=server)

        self.config.suppress_callback_exceptions = True
        Kritter._kapp_var.set(self)

        self.main_div = html.Div([], id="_main") 
        self.title = "Kritter"

        # Deal with media paths
        self.media_path = [os.path.join(BASE_DIR, MEDIA_DIR)]

        # Setup route for media 
        @self.server.route(os.path.join(MEDIA_URL_PATH,'<path:file>'))
        async def media(file):
            filepath = file_in_path(self.media_path, file)
            if filepath:
                return await send_file(filepath)
            # If can't find, just return empty string
            return ''

        # Use default favicon if none is provided
        @self.server.route('/favicon.ico')
        async def favicon():
            # Look at each path, return first hit
            filepath = file_in_path(self.media_path, 'favicon.ico')
            if filepath:
                return await send_file(filepath, mimetype='image/x-icon')

        layout = self.main_div
        # Trigger setting of Dash.index_string
        self.style = ''

        # Call Dash setter for layout explicitly.
        Dash.layout.fset(self, layout)
    
    def redirect(self, url):
        return html.Meta(httpEquiv="refresh", content=f"0; url='{url}'")     
    
    def out_main(self, val):
        return [Output("_main", "children", val)]

    def out_redirect(self, url):
        return self.out_main(self.redirect(url))

    @staticmethod
    def icon(icon_name, padding=5):
        className = "fa" if icon_name is None else "fa fa-" + icon_name 
        return html.Span(className=className, style={"padding-right": str(padding) + "px"})

    @staticmethod
    def new_id(name='_k'):
        _id = name + str(Kritter._id_count)
        Kritter._id_count += 1
        return _id    

    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, _style):
        self._style = _style
        _style = KRITTER_STYLE + _style
        self.index_string = index_string(_style)

    
    # Kcomponents need to be "unwrapped" to put the underlying Dash components
    # into the layout.  This is a convenience -- so we can treat Kcomponents 
    # like Dash components.  We just need to make sure that any 
    # Kcomponents that make into the layout need to be unwrapped before they can be 
    # used by Dash. 
    @staticmethod
    def unwrap(layout):
        from .kdialog import Kdialog
        if hasattr(layout, "children"):
            layout.children = Kritter.unwrap(layout.children)
        if isinstance(layout, (Kcomponent, Kdialog)):
            layout = layout.layout = Kritter.unwrap(layout.layout)
        elif isinstance(layout, (list, tuple)):
            if isinstance(layout, tuple):
                layout = list(layout)
            for i in range(len(layout)):
                layout[i] = Kritter.unwrap(layout[i])
        return layout

    @property
    def layout(self):
        return self.main_div.children

    @layout.setter
    def layout(self, layout):
        self.push_mods(Output(self.main_div.id, "children", Kritter.unwrap(layout)))

    def get_media_url(self, filename):
        return os.path.join(MEDIA_URL_PATH, filename)

    def run(self, port=None):    
        if port is None:
            if os.geteuid()==0: # root permissions
                port = 80 # default http port, only available with root permissions
            else:  
                port = PORT
        self.enable_dev_tools(debug=False, dev_tools_client_reload=True)
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        asyncio.get_event_loop().run_until_complete(serve(self.server, config))
        #self.run_server(debug=False, use_reloader=False, dev_tools_client_reload=True, host='0.0.0.0', port=port)

