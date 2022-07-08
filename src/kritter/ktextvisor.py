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

SOCKET = 50000
MAX_CLIENTS = 5
AUTHKEY = b'KtextVisor'
CONTEXT_TIMEOUT = 60*5 # seconds


class _KtextManager(BaseManager):
    pass    

def callback_client(self):
    print("callback_client")
    def wrap_func(func):
        try:
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
            self.callback_server(socket)        
    return wrap_func

# The result of the proxied functions is multiprocessor.managers.AutoProxy type, 
# so we convert to native type with _getvalue... this may be a bug in Python 3.7.
def get_func(callback):
    def func(*args, **kwargs):
        res = callback(*args, **kwargs)
        return res._getvalue() 
    return func

def callback_server(self, socket):
    c = _KtextManager(address=('localhost', socket), authkey=AUTHKEY)
    c.connect()
    self.callbacks.append(get_func(c.call_callbacks))


def KtextVisor(text_client=None):
    try:
        if text_client is None:
            raise Exception() # branch below
        tv = _KtextVisor(text_client)
        tm = _KtextManager(address=('', SOCKET), authkey=AUTHKEY)
        _KtextManager.register('KtextVisor', callable=lambda:tv)
        print("Running KtextVisor server...")
        _KtextManager.register('call_callbacks')
        tv.callback_server = MethodType(callback_server, tv) 
        tv.server = tm.get_server()       
        tv.thread = Thread(target=tv.server.serve_forever).start()
        return tv
    except:
        print("Running KtextVisor client...")
        _KtextManager.register('KtextVisor')
        # This will throw an exception if server isn't running.  Client code can catch 
        # and retry if needed. 
        tm = _KtextManager(address=('localhost', SOCKET), authkey=AUTHKEY)
        tm.connect()
        tv = tm.KtextVisor()
        tv.callback_receive = MethodType(callback_client, tv)
        return tv

def format_content(content):
    if isinstance(content, (str, Image)):
        return [content] 
    elif isinstance(content, dict):
        res = ""
        for k, v in content.items():
            if res:
                res += '\n'
            res += f"{k}: {v}"
        return [res]
    elif isinstance(content, (list, tuple)):
        res = []
        for i in content:
            r = format_content(i)
            if isinstance(r[0], str) and len(res) and isinstance(res[-1], str):
                res[-1] += '\n' + r[0] # combine strings
                res += r[1:] # then append rest of content
            else:
                res += r 
        return res 
    else:
        raise RuntimeError(f"Can only process Image, str, dict, tuple, and list -- not {type(content)}.")

class _KtextVisor():
    def __init__(self, text_client):
        self.text_client = text_client
        self.callbacks = [self.intrinsic_callback]
        self.context = {}
        self.lock = Lock()
        @self.text_client.callback_receive()
        def func(sender, message):
            print(f"*** Received: {message} from {sender}.")
            words = message.split()
            context = self.pre_handle_context(sender)
            responses = self.call_callbacks(sender, words, context)
            self.post_handle_context(sender, responses)
            self.send_responses(sender, responses)

    def close(self):
        try:
            self.server.stop_event.set()
            self.thread.join()
        except:
            pass

    def callback_receive(self):
        def wrap_func(func):
            self.callbacks.append(func)
        return wrap_func

    def call_callbacks(self, sender, words, context):
        responses = []
        for c in self.callbacks.copy():
            try:
                response = c(sender, words, context)
                print("*** response", response, type(response))
                if isinstance(response, Response):
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
            return self.context[sender][1]
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
                context = self.context[sender]
            except:
                context = []
        if context==[]:
            try:
                del self.context[sender]
            except: 
                pass
        else:
            self.context[sender] = (t, context)

                        
    def send_responses(self, sender, responses):
        content = [r.content for r in responses]
        content = format_content(content)
        for c in content:
            with self.lock:
                if isinstance(c, str):
                    self.text_client.text(sender, c)
                else: # must be an image    
                    self.text_client.image(sender, c.image)

    def intrinsic_callback(self, sender, words, context):
        if not words:
            return
        if words[0]=="subscribe":
            pass
        elif words[0]=="unsubscribe":
            pass 

    # send to all interested recipients
    def notify(self):
        pass 


# context = None means no change to context, context = [] means reset context
class Response:
    def __init__(self, content, context=None, claim=True):
        self.content = format_content(content)
        self.context = context
        self.claim = claim

class Image:
    def __init__(self, image):
        self.image = image
