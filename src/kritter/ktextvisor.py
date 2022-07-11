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
from types import MethodType
from threading import Thread, Lock
from multiprocessing.managers import BaseManager
import fnmatch
from .ktextclient import Image

SOCKET = 50000
MAX_CLIENTS = 5
AUTHKEY = b'KtextVisor'
CONTEXT_TIMEOUT = 60*5 # seconds


class _KtextManager(BaseManager):
    pass    

def callback_client(self, prepend=False):
    def wrap_func(func):
        try:
            if prepend:
                self.callbacks.insert(0, func)
            else:
                self.callbacks.append(func)
        except:
            self.callbacks = [func]
            for i in range(MAX_CLIENTS+1):
                try:
                    socket = SOCKET+i+1
                    fm = _KtextManager(address=('', socket), authkey=AUTHKEY)
                    self.server = fm.get_server()
                    call_callbacks = MethodType(_KtextVisor.call_callbacks, self)
                    _KtextManager.register('call_callbacks', callable=call_callbacks)
                    break
                except:
                    if i>=MAX_CLIENTS:
                        raise RuntimeError("There seem to be too many clients...")
                    continue
            self.thread = Thread(target=self.server.serve_forever).start()
            # Client registers with server
            self.callback_server(socket, self.client_name, prepend)        
    return wrap_func

# The result of the proxied functions is multiprocessor.managers.AutoProxy type, 
# so we convert to native type with _getvalue... this may be a bug in Python 3.7.
def get_func(callback):
    def func(*args, **kwargs):
        res = callback(*args, **kwargs)
        return res._getvalue() 
    return func

def callback_server(self, socket, client_name, prepend):
    c = _KtextManager(address=('localhost', socket), authkey=AUTHKEY)
    c.connect()
    func = get_func(c.call_callbacks)
    func.client_name = client_name
    self.callbacks = [callback for callback in self.callbacks if not hasattr(callback, "client_name") or callback.client_name!=client_name]
    if prepend:
        self.callbacks.insert(0, func)
    else:
        self.callbacks.append(func)

# Pass in pointer to KtextClient if server or client_name if client
def KtextVisor(text_client=""):
    try:
        if isinstance(text_client, str):
            raise Exception() # branch to client code below
        tv = _KtextVisor(text_client)
        tm = _KtextManager(address=('', SOCKET), authkey=AUTHKEY)
        _KtextManager.register('KtextVisor', callable=lambda:tv)
        _KtextManager.register('call_callbacks')
        tv.callback_server = MethodType(callback_server, tv) 
        tv.server = tm.get_server()       
        tv.thread = Thread(target=tv.server.serve_forever).start()
        return tv
    except:
        _KtextManager.register('KtextVisor')
        _KtextManager.register('text_client')
        # This will throw an exception if server isn't running.  Client code can catch 
        # and retry if needed. 
        tm = _KtextManager(address=('localhost', SOCKET), authkey=AUTHKEY)
        tm.connect()
        tv = tm.KtextVisor()
        tv.client_name = text_client
        tv.callback_receive = MethodType(callback_client, tv)
        tv.close = MethodType(_KtextVisor.close, tv)
        return tv

def format_content(content):
    if isinstance(content, (str, Image, dict)):
        return [content] 
    elif isinstance(content, (list, tuple)):
        res = []
        for i in content:
            r = format_content(i)
            if isinstance(r[0], str) and len(res) and isinstance(res[-1], str):
                res[-1] += '\n' + r[0] # combine strings
                res += r[1:] # then append rest of content
            elif isinstance(r[0], dict) and len(res) and isinstance(res[-1], dict):
                r[0].update(res[-1]) # update backwards because of nature of ordering
                res[-1] = r[0]
                res += r[1:] 
            else:
                res += r 
        return res 
    else:
        raise RuntimeError(f"Can only process Image, str, dict, tuple, and list -- not {type(content)}.")

def format_dict(content):
    justify = max([len(k) for k, v in content.items()]) + 2
    res = ""
    for k, v in content.items():
        if res:
            res += '\n'
        k += ':'
        res += k.ljust(justify) + v
    return res    

class _KtextVisor:
    def __init__(self, text_client):
        self.text_client = text_client
        self.callbacks = [self.native_callback]
        self.context = {}
        self.lock = Lock()
        @self.text_client.callback_receive()
        def func(message, sender):
            print(f"*** Received: {message} from {sender}.")
            words = message.split()
            context = self.pre_handle_context(sender)
            responses = self.call_callbacks(words, sender, context)
            self.post_handle_context(sender, responses)
            if words[0].lower()!="help":
                claimed = bool([r.claim for r in responses if r.claim])
                if not claimed:
                    responses += [Response('Try "help".')]
            self.send_responses(sender, responses)

    def close(self):
        try:
            self.server.stop_event.set()
            self.thread.join()
        except:
            pass

    def callback_receive(self, prepend=False):
        def wrap_func(func):
            if prepend:
                self.callbacks.insert(0, func)
            else:
                self.callbacks.append(func)
        return wrap_func

    def call_callbacks(self, words, sender, context):
        responses = []
        for c in self.callbacks.copy():
            try:
                response = c(words, sender, context)
                if response==[]:
                    continue
                elif isinstance(response, Response):
                    responses += [response]
                elif isinstance(response, list) and isinstance(response[0], Response):
                    responses += response
                elif response:
                    responses += [Response(response)]
                claimed = bool([r.claim for r in responses if r.claim])
                if claimed:
                    break
            except ConnectionRefusedError:
                self.callbacks.remove(c)
        return responses
    
    def pre_handle_context(self, sender):
        t = time.time()
        # c is a tuple: (timestamp, tags):
        self.context = {_sender: c for _sender, c in self.context.items() if t-c[0]<CONTEXT_TIMEOUT}
        try:
            return self.context[sender['id']][1]
        except:
            return []

    def post_handle_context(self, sender, responses):
        t = time.time()
        contexts = [r.context for r in responses]
        contexts = [c for c in contexts if c is not None]
        if len(contexts):
            context = set(contexts[-1])
        else:
            try:
                context = self.context[sender['id']][1]
            except:
                context = []
        if context==[]:
            try:
                del self.context[sender['id']]
            except: 
                pass
        else:
            self.context[sender['id']] = (t, context)

                        
    def send_responses(self, sender, responses):
        content = [r.content for r in responses] # extract content
        content = format_content(content) # combine strs and dicts
        content = [format_dict(c) if isinstance(c, dict) else c for c in content] # format dicts into strs
        content = format_content(content) # combine strs again
        with self.lock:
            self.text_client.send(content, sender)

    def native_callback(self, words, sender, context):
        pass
        # this where subscribe goes

    def send(self, msg, to):
        if to is None:
            pass
            # send to all interested parties 
        else:
            self.text_client.send(msg, to)

class KtextVisorTable:
    def __init__(self, table, help_claim=False):
        self.table = table
        self.help_claim = help_claim

    def lookup(self, words, sender, context):
        if words[0].lower()=="help":
            return Response({k: v[1] for k, v in self.table.items() if v[1]}, claim=self.help_claim)
        else:
            for k, v in self.table.items():
                if fnmatch.fnmatch(words[0], k):
                    return v[0](words, sender, context)

# context = None means no change to context, context = [] means reset context
class Response:
    def __init__(self, content, context=None, claim=True):
        self.content = format_content(content)
        self.context = context
        self.claim = claim

