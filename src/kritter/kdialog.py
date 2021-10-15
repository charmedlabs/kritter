import dash_devices 
from functools import wraps
import dash_html_components as html
from dash_devices import callback_context
from dash_devices.dependencies import Input, Output
import dash_bootstrap_components as dbc
from .kritter import Kritter

class Kdialog:

    def __init__(self, **kwargs):
        self.kapp = kwargs['kapp'] if 'kapp' in kwargs else Kritter.kapp
        if 'title' in kwargs:
            self.header = dbc.ModalHeader(kwargs['title'], id=Kritter.new_id())
        else:
            self.header = None
        left_footer = kwargs['left_footer'] if 'left_footer' in kwargs else None
        right_footer = kwargs['right_footer'] if 'right_footer' in kwargs else None
        size = kwargs['size'] if 'size' in kwargs else None
        layout = kwargs['layout'] if 'layout' in kwargs else [] 
        backdrop = kwargs['backdrop'] if 'backdrop' in kwargs else True 
        shared = kwargs['shared'] if 'shared' in kwargs else False
        # The displaying of dialogs is probably more natural if it's not shared.   
        self.service = dash_devices.Services.SHARED if shared else None
        self.id = kwargs['id'] if 'id' in kwargs else Kritter.new_id('dialog')
        close_button = dbc.Button([Kritter.icon("close"), "Close"], id=self.id+"-cb", className="ml-auto")
        fc = [html.Div(close_button)]
        if 'close_button' in kwargs:
            if kwargs['close_button']==False:
                close_button = None
                fc = []
            else:
                close_button.children = kwargs['close_button']
        if right_footer:
            fc.insert(0, html.Div(right_footer, className="ml-auto"))             
        if left_footer:
            fc.insert(0, html.Div(left_footer, className="mr-auto")) 
        self.footer = dbc.ModalFooter(fc) if fc else None   

        # Create body and add out layout elements to it.
        self.main = dbc.ModalBody(id=Kritter.new_id())
        self.main.children = layout

        # The layout is just the Modal object.
        self.layout = dbc.Modal([self.header]+[self.main]+[self.footer], backdrop=backdrop, id=self.id)
        # Add size if needed.
        if size is not None:
            self.layout.size = size

        # Connect close button to dialog.
        if close_button is not None:
            @self.kapp.callback(Output(self.id, "is_open"), [Input(close_button.id, "n_clicks")], service=self.service)
            def func(clicks):
                if clicks is not None:
                    return False

        # We create the callback regardless of whether callback_view is
        # registered or not because there is a bug(?) such that if you dismiss a
        # dialog by clicking outside dialog and then refresh the page, the dialog comes 
        # back.  Registering a callback prevents this from happening.           
        @self.kapp.callback(None, [Input(self.id, "is_open")], service=self.service)
        def func(open_):
            pass


    def callback_view(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, "is_open")], state, self.service)
            def _func(*args):
                # We're part of a callback chain with the close button, so we will get 
                # called upon initialization with open=None, so we should exclude.
                if args[0] is not None:  
                    return func(*args)
        return wrap_func

    def out_open(self, open_):
        return [Output(self.id, "is_open", open_)]        


class KyesNoDialog(Kdialog):
    def __init__(self, **kwargs):
        yes = kwargs["yes"] if "yes" in kwargs else "Yes"
        no = kwargs["no"] if "no" in kwargs else "No"
        self.callback_func = None
        yes_button = dbc.Button(yes, id=Kritter.new_id())
        no_button = dbc.Button(no, id=Kritter.new_id(), style={"margin-left": "10px"})
        super().__init__(**kwargs, close_button=False, right_footer=html.Div([yes_button, no_button]))

        @self.kapp.callback(None,
            [Input(yes_button.id, "n_clicks"), Input(no_button.id, "n_clicks")], service=self.service)
        def _func(yes, no):
            button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
            res = None
            if self.callback_func:
                res = self.callback_func(button_id==yes_button.id)
            _res = self.out_open(False)  
            if not res:
                return _res 
            elif isinstance(res, (tuple, list)):
                if isinstance(res, tuple):
                    res = list(res)
                return res + _res 
            elif isinstance(res, Output):
                return [res] + _res

    def callback_response(self):
        def wrap_func(func):
            self.callback_func = func
        return wrap_func

class KokDialog(Kdialog):
    def __init__(self, **kwargs):
        ok = kwargs["ok"] if "ok" in kwargs else "OK"
        ok_button = dbc.Button(ok, id=Kritter.new_id())
        super().__init__(**kwargs, close_button=False, right_footer=ok_button)

        @self.kapp.callback(Output(self.id, "is_open"),
            [Input(ok_button.id, "n_clicks")], service=self.service)
        def _func(ok):
            if ok is not None:
                return False

class KsideMenuItem:
    def __init__(self, name, action_object, icon=None, target=None, kapp=None):

        if kapp is None:
            kapp = Kritter.kapp
        children = [name]
        if icon is not None:
            children.insert(0, Kritter.icon(icon))
        self.dialog = None
        self.layout = dbc.DropdownMenuItem(children, 
            id=Kritter.new_id(), className="_k-menu-button-item")
        if isinstance(action_object, str):
            if target is None:
                script = f"""
                function(value) {{
                    window.location.href = "{action_object}"; 
                }}
                """
            else:
                script = f"""
                function(value) {{
                    window.open("{action_object}", "{target}");
                }}
                """
            kapp.clientside_callback(script,
                Output("_none", Kritter.new_id()), [Input(self.layout.id, 'n_clicks')]
            )
        elif isinstance(action_object, Kdialog):
            self.dialog = action_object
            @kapp.callback(None, 
                [Input(self.layout.id, "n_clicks")], service=self.dialog.service)
            def func(clicks):
                if clicks is not None:
                    return action_object.out_open(True)
