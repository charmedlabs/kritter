import sys
import os
import subprocess
import time
import tempfile
from termcolor import colored
from threading import Thread

EXEC_VAR = '_RESETEXEC'
EXIT_CODE = 0xc1

class ResetExec:

    def __init__(self):
        if os.environ.get(EXEC_VAR) is None:
            #print('**** start loop')
            sys.exit(self._restart_loop())
        #print('**** init exit')

    def _restart_loop(self):
        # If we want to save memory, we can try to unimport all unnecessary modules here.
        # ... but I haven't found a way to do this and the amount of savings is unclear.

        command = [sys.executable] + sys.argv

        new_environ = os.environ.copy()
        # Create unique temporary filename
        fd, exec_file = tempfile.mkstemp()
        os.close(fd) # No need to keep open
        new_environ[EXEC_VAR] = exec_file

        while True:
            #print("**** running", command)
            try:
                cp = subprocess.run(command, env=new_environ)
            except: 
                print(colored("\n\nProgram has exited.", "green"))
                return 0
            #print('**** exit', cp.returncode)
            if cp.returncode==EXIT_CODE:
                # Check exec_file
                with open(exec_file) as f:
                    _command = f.read()
                # Replace command with new command and continue.
                if len(_command):
                    command = _command
            else:
                # This exit is legit, so exit supervisor too.
                return cp.returncode

    def _exit(self, delay=0):
        #print("**** _exit")
        time.sleep(delay)
        #print('**** exiting')
        os._exit(EXIT_CODE)
        #sys.exit(EXIT_CODE)

    def _resetexec(self, command, block, delay):
        if command is not None:
            exec_file = os.environ.get(EXEC_VAR)
            # We should always have an exec file in the env. 
            if exec_file is None:
                raise RuntimeError("Unable to restart because no exec file was provided.") 
            # Write command to temp exec file
            with open(exec_file, 'w') as f:
                f.write(command)
        if not block:
            thread = Thread(target=self._exit, args=(delay))
            thread.start()
        else:
            self._exit(delay)

    def exec(self, command, block=False, delay=0):
        _resetexec(command, block, delay)

    def restart(self, block=False, delay=0):
        _resetexec(None, block, delay)
