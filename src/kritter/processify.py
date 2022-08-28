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
from multiprocessing import Process

SOCKET = 56579

class _Manager(BaseManager): 
    pass

def _server(Cls, args, socket):
    obj = Cls(*args)
    _Manager.register('server', callable=lambda: obj)
    manager = _Manager(address=('', socket), authkey=Cls.__name__.encode())
    server = manager.get_server()
    server.serve_forever()

# This class proxies a class instance in a separate process.
class Processify:

    def __init__(self, Cls, args=(), socket=SOCKET):
        # Start server
        self.process = Process(target=lambda: _server(Cls, args, socket))
        self.process.start() 

        # Setup and connect to server
        _Manager.register('server')
        manager = _Manager(address=('localhost', socket), authkey=Cls.__name__.encode())
        # Connecting to server might need to wait a bit...
        while True:
            try:
                manager.connect()
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        self.server = manager.server()

    def __getattr__(self, attr):
        return getattr(self.server, attr)    

    def close(self):
        self.process.terminate()
        self.process.join()
