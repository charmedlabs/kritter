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
# SharedMemoryManager would be better than BaseManager for Python v3.8 or greater
from multiprocessing.managers import BaseManager 

SOCKET = 56579

class _Manager(BaseManager): 
    pass

def _server(Cls, args, socket):
    obj = Cls(*args)
    def func():
        return obj
    _Manager.register('server', callable=func)

# This class proxies a class instance in a separate process.  
# It's remarkable how little code takes!  
class Processify:

    def __init__(self, Cls, args=(), socket=SOCKET):
        # Setup and connect to server
        _Manager.register('server')
        self.manager = _Manager(address=('localhost', socket), authkey=Cls.__name__.encode())
        self.manager.start(initializer=lambda: _server(Cls, args, socket))
        # Connecting to server might need to wait a bit...
        while True:
            try:
                self.manager.connect()
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        self.server = self.manager.server()

    def __getattr__(self, attr):
        return getattr(self.server, attr)    

    def close(self):
        self.manager.shutdown()
        self.manager.join()
