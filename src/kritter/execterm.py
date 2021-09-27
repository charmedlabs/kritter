import time
from threading import Thread
from urllib.parse import urlparse
from urllib.request import urlopen
import dash_html_components as html
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kcomponent import default_style
from .kdialog import Kdialog
from .kritter import Kritter, run_kterm

DEFAULT_PORT = 5010
DIALOG_ID = "_execterm"
DIALOG_DIV_ID = DIALOG_ID + "-div"

class ExecTerm:

    def __init__(self, kapp=None):
        if kapp is None:
            kapp = Kritter.kapp
        self.kapp = kapp
        self.thread = None
        self.proc = None
        self._callback_done = None
        self.layout = html.Div([], id=DIALOG_DIV_ID)

        # Since callbacks need to all be created before running the server, we 
        # create a dummy dialog that will add the callbacks that will be
        # used later by self.exec.
        self.dialog = Kdialog(id=DIALOG_ID, shared=True)

        # The callback_view callback does most of the work
        @self.dialog.callback_view()
        def func(open):
            if not open:
                # No need for a lock here.
                if self.proc:
                    self.proc.kill()
                    self.proc = None


    def exec(self, **kwargs):
        kwargs.update({"kapp": self.kapp, "id": DIALOG_ID, "shared": True})
        self.dialog = Kdialog(**kwargs)
        self.command = kwargs['command'] if 'command' in kwargs else 'bash'
        self.port = kwargs['port'] if 'port' in kwargs else DEFAULT_PORT
        logfile = kwargs['logfile'] if 'logfile' in kwargs else None
        height = kwargs['height'] if 'height' in kwargs else 400

        self.iframe = html.Iframe(id=Kritter.new_id(), style={"height": str(height)+"px", "width": "100%", "border": 0})
        self.iframe_div = html.Div(self.iframe, id=Kritter.new_id())

        self.dialog.main.children = [self.iframe_div]

        # Add ourself to the layout
        self.kapp.push_mods(Output(self.layout.id, "children", self.dialog.layout))

        # Note, dash_devices will prevent callbacks from stepping on each other 
        # such that we're not starting one process while killing another, etc. 
        # So no need for a lock here.
        # Start kterm process (doesn't block)
        self.proc = run_kterm(self.port, self.command, logfile=logfile)
        # Run thread to wait for process to exit
        self.thread = Thread(target=self.wait_proc)
        self.thread.start()
        # Wait for page to become active
        while True: 
            try:
                urlopen('http://localhost:' + str(self.port))
                break
            except:
                time.sleep(0.25)

        # Set src for all clients (they aren't necessarily the same)
        # This will cause the iframe to try to load the page
        for c in self.kapp.clients:
            url = urlparse(c.origin)
            # use our port
            new_src = url._replace(netloc=url.hostname+":"+str(self.port)).geturl()
            self.kapp.push_mods(Output(self.iframe.id, "src", new_src), c)
        # show dialog
        return self.dialog.out_open(True)


    def callback_done(self, func):
        self._callback_done = func

    def wait_proc(self):
        # wait for process to exit
        self.proc.wait()
        # close dialog because we're done
        self.kapp.push_mods(Output(self.dialog.id, "is_open", False))
        # Indicate we're done
        if self._callback_done is not None:
            self._callback_done()

