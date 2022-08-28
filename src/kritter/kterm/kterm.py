#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

#!/usr/bin/env python3
from quart import Quart, Blueprint, websocket, copy_current_websocket_context, render_template, send_file
from hypercorn.config import Config
from hypercorn.asyncio import serve
from threading import Thread  
import pty
import os
import signal
import termios
import struct
import fcntl
import asyncio
import json
import argparse
import logging
import time
from termcolor import colored

# For some reason setting logger to debug breaks things
logger = logging.getLogger(__name__)
from kritter.util import set_logger_level
#set_logger_level(logger, logging.DEBUG)

PORT = 5000

COLORS = \
'''
GREEN='\033[0;32m'
NC='\033[0m'
'''

NO_RESTART = COLORS + \
'''
{}
echo -e "\n$GREEN""Process has exited.""$NC"
sleep 2
'''

RESTART = COLORS + \
'''
trap '' 2
while true
do 
  {} 
  echo -e "\n$GREEN""Process has exited.""$NC"
  echo -e "$GREEN""Restarting...""$NC\n"
done
'''

RESTART_QUERY = COLORS + \
'''
trap '' 2
while true
do 
  {} 
  echo -e "\n$GREEN""Process has exited.""$NC"
  read -p "$GREEN""Press enter to restart.""$NC"
  echo
done
'''

class Client:
    def __init__(self, fd):
        self.fd = fd
        self.queue = asyncio.Queue()
        self.rows = 0
        self.cols = 0


def exception_handler(loop, context):
    if 'future' in context:
        task = context['future']
        task.print_stack()


class Kterm:
    
    _count = 0

    def __init__(self, command, single=False, script=NO_RESTART, name="", logfile="", favicon=None, wfc_thread=True, protect=None):
        self.command = command
        self.script = script
        self.name = name
        self.logfile = logfile
        self.clients = []
        self.scroll_back = 1000
        self.buffer = ''
        self.buffer_max_size = self.scroll_back*40
        self.single_fd = None
        self.single_pid = None
        self.single = single
        self.wfc_thread = wfc_thread
        self.server = Blueprint(f'kterm{Kterm._count}', __name__, template_folder='.', static_folder='.', static_url_path='')
        Kterm._count += 1
        if favicon is None:
            self.favicon = os.path.join(self.server.root_path, 'static', 'favicon.ico')
        else:
            self.favicon = favicon
        if protect is None:
            def null(func):
                return func
            self.protect = null
        else:
            self.protect = protect
        self.loop = asyncio.get_event_loop()
        self.loop.set_exception_handler(exception_handler)

        @self.server.route('/')
        @self.protect
        async def root():
            return await render_template("kterm.html")

        @self.server.route('/favicon.ico')
        async def favicon():
            return await send_file(self.favicon, mimetype='image/x-icon')

        @self.server.websocket('/_kterm')
        @self.protect
        async def ws():
            logger.debug('spawn')
            await self.connect()

        # If no command, we are going to "term-ify" the existing process
        if self.command is None:
            self.single = True 
            self.start_single_process()
            # One side of the fork becomes the server
            if self.single_pid:
                self.run()
                # Don't fall through
                os._exit(0)

    def run(self, port=PORT):
        app = Quart("kterm")
        app.register_blueprint(self.server)   
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        self.loop.run_until_complete(serve(app, config))
        # Clean up single_pid so we can free up wait_for_child thread
        # and exit cleanly.
        if self.single_pid:
            os.kill(self.single_pid, signal.SIGTERM)

    def set_winsize(self, fd, row, col):
        logger.debug('set_winsize ' + str(row) + str(col))
        winsize = struct.pack("HHHH", row, col, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    async def send_client(self, client):
        title = self.name if self.name else self.command.split()[0]
        await websocket.send(json.dumps({"id": "title", "data": title}))
        while True:
            data = await client.queue.get()
            await websocket.send(json.dumps(data))

    async def recv_client(self, client):
        while True:
            data = await websocket.receive()
            data = json.loads(data)
            id_ = data['id']
            data = data['data']
            fd = client.fd if client.fd is not None else self.single_fd
            if id_=='input':
                os.write(fd, data.encode())
            elif id_=='resize':
                client.rows = data["rows"]
                client.cols = data["cols"]
                if self.single_fd is None or client is self.clients[0]: 
                    self.set_winsize(fd, client.rows, client.cols)

    def reader_callback(self, client):
        if client is not None:
            try:
                data = os.read(client.fd, 0x8000).decode()
                # If no command, go ahead and pass-thru stdout
                if self.command is None:
                    print(data, end="")
            except IOError:
                self.loop.remove_reader(client.fd)
                return
            client.queue.put_nowait({"id": "output", "data": data})
        else:
            try:
                data = os.read(self.single_fd, 0x8000).decode()
                # If no command, go ahead and pass-thru stdout
                if self.command is None:
                    print(data, end="")
            except IOError:
                self.loop.remove_reader(self.single_fd)
                return
            # Print output of child process. Should this be a command line option?
            for client in self.clients:
                client.queue.put_nowait({"id": "output", "data": data})
            self.buffer += data
            if len(self.buffer)>self.buffer_max_size:
                self.buffer = self.buffer[int(0.2*self.buffer_max_size):]

    def fork(self):
        logger.debug("fork")
        pid, fd = pty.fork()
        if pid==0:
            try:
                if self.logfile:
                    os.execvp("script", ("script", "-f", self.logfile, "-c", self.script.format(self.command)))
                elif self.command is not None:
                    os.execvp("bash", ("bash", "-c", self.script.format(self.command)))
                # else fall through, continue execute current process
            except Exception as e:
                print(f"Unable to start: {e}")
        return pid, fd

    def start_single_process(self, command=None):
        if not self.single:
            raise RuntimeError("This is only for single process option.")
        if command:
            self.command = command

        self.single_pid, self.single_fd = self.fork()
        if self.single_pid==0:
            return 0
        # Spawn a thread to wait for child to exit, then return exit code.
        if self.wfc_thread:
            wait_thread = Thread(target=self.wait_for_child)
            wait_thread.start()
        self.loop.add_reader(self.single_fd, self.reader_callback, None)
        return self.single_pid

    async def connect(self):
        pid, fd = None, None
        if self.single and self.single_fd is None:
            self.start_single_process()

        if not self.single:
            pid, fd = self.fork()
            client = Client(fd)
            self.loop.add_reader(fd, self.reader_callback, client)
        else:
            client = Client(None)
            client.queue.put_nowait({"id": "output", "data": self.buffer})

        self.clients.append(client)

        try:
            sender = asyncio.create_task(copy_current_websocket_context(self.send_client)(client))
            receiver = asyncio.create_task(copy_current_websocket_context(self.recv_client)(client))

            await asyncio.gather(sender, receiver)

        except asyncio.CancelledError:
            pass
        finally:
            # Pass window dimensions onto the next client.
            if self.single_fd is not None and client is self.clients[0] and len(self.clients)>1:
                self.set_winsize(self.single_fd, self.clients[1].rows, self.clients[1].cols)
            self.clients.remove(client)
            if fd is not None:
                self.loop.remove_reader(fd)
            if pid is not None:
                # Kill child.
                logger.debug("kill")
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
                obj = os.waitid(os.P_PID, pid, os.WEXITED)

    def wait_for_child(self):
        logger.debug("waiting_for_child...")
        obj = os.waitid(os.P_PID, self.single_pid, os.WEXITED)
        # Wait for things to propagate from readers, etc.
        logger.debug("done waiting_for_child")
        os._exit(obj.si_status)

    def print(self, msg):
        for client in self.clients:
            client.queue.put_nowait({"id": "output", "data": msg+"\n\r"})
             
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A terminal that runs any command-line program and renders it in your browser.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", default=PORT, help="port to run server on")
    parser.add_argument("-s", action='store_true', help="single occurence of process")
    parser.add_argument("-r", action='store_true', help="restart when process exits")
    parser.add_argument("-rq", action='store_true', help="query to restart when process exits")
    parser.add_argument("-c", default="bash", help="Command to run in the terminal")
    parser.add_argument("-n", default="", help="Name of the console")
    parser.add_argument("-l", default="", help="Log file for dumping term text")
    args = parser.parse_args()
    script = NO_RESTART
    if args.r:
        script = RESTART 
    if args.rq:
        script = RESTART_QUERY

    term = Kterm(args.c, args.s, script, args.n, args.l)
    term.run(args.p)
