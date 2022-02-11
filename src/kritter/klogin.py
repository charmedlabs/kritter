#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os  
import urllib.parse
from quart import redirect, session, request, send_file
from functools import wraps

# This is an int with all bits set -- full permissions. 
# Python3 supports unbounded ints in case you need more than 64 permission bits.
PMASK_MAX = (1<<64)-1
# Smallest non-zero integer
PMASK_MIN = 1

def authorize(username, password):
    return username=="admin" and password=="admin"

class Klogin:

    def __init__(self, kapp, content_dir=None, secret="change me!"):
        self.kapp = kapp
        self.kapp.server.secret_key = secret
        self.authorize_func = authorize
        if content_dir is None:
            content_dir = os.path.join(kritter.BASE_DIR, "login")

        self.protect_socket()
        self.protect_path("/")

        @self.kapp.callback_authorize_output
        def func(client, output):
            # If output is _main.children, it's a redirect page to login, 
            # so don't block. 
            # Client is none when the callback is part of an initial callback chain, 
            # or dispatch chain initiated by Dash, so don't block.
            return client is None or client.authentication or output=="_main.children"

        @self.kapp.server.route('/login', defaults={'qs': ""})        
        @self.kapp.server.route('/login/', defaults={'qs': ""})
        @self.kapp.server.route('/login/<path:qs>')
        async def login(qs):
            filepath = os.path.join(content_dir, qs)
            if os.path.isfile(filepath):
                return await send_file(filepath)
            d = urllib.parse.parse_qs(qs)
            try:
                session['path'] = d['path'][0]
            except:
                pass
            filepath = os.path.join(content_dir, "login.html")
            return await send_file(filepath)

        @self.kapp.server.route('/logout')
        async def logout():
            session['username'] = ""
            session['password'] = "" 
            session['path'] = "/"
            for c in self.kapp.clients:
                c.authentication = 0
            filepath = os.path.join(content_dir, "login.html")
            return await send_file(filepath)

        @self.kapp.server.route('/login', methods=['POST'])
        async def login_post():
            form = await request.form
            username = form['username']
            password = form['password']
            session['username'] = username
            session['password'] = password 
            if self.authorize_func(username, password):
                session.permanent = False
                path = session['path'] if 'path' in session else '/'
            else:
                path = '/login' # retry
            return redirect(path) 

    def callback_authorize(self, func):
        self.authorize_func = func

    # This is a double-wrap so we can inject a custom permission mask into the 
    # the authentication calculation.
    def protect(self, permission_mask=PMASK_MAX):    
        def wrap(func):
            @wraps(func)
            async def _wrap(*args, **kwargs):
                s = session.copy()
                try:
                    if self.authorize_func(s['username'], s['password'])&permission_mask:
                        return await func(*args, **kwargs)
                except:
                    pass
                try:
                    # Websocket routes will throw an exception, so we'll return None.
                    path = request.full_path 
                except:
                    return None
                # Non-websocket routes will create a login url with the path encoded, 
                # So we can return later.  
                qs = urllib.parse.urlencode({"path": f"{path}"})
                path = f"/login/{qs}"
                return redirect(path)
            # Need to change name or quart complains
            _wrap.__name__ = func.__name__
            return _wrap
        return wrap


    def protect_socket(self):
        original_func = self.kapp.server.view_functions['update_component_socket']
        async def wrap():
            try:
                s = session.copy()
                await original_func(self.authorize_func(s['username'], s['password']), s['username'])
                return
            except:
                await original_func(0)
        self.kapp.server.view_functions["update_component_socket"] = wrap

    def protect_path(self, path, permission_mask=PMASK_MAX):
        for rule in self.kapp.server.url_map.iter_rules():
            if rule.rule==path or rule.rule==path+'/':
                original_func = self.kapp.server.view_functions[rule.endpoint]
                self.kapp.server.view_functions[rule.endpoint] = self.protect(permission_mask)(original_func)
                break

