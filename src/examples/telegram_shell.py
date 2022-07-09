import time
from kritter.ktextvisor import KtextVisor, Response, Image
import os
import subprocess
import threading
import signal

# The way context is set up, we'd need one shell instance per user....
class Shell:
    def __init__(self):
        self.text_visor = KtextVisor("shell")
        self.sender = None
        self.process = None
        @self.text_visor.callback_receive()
        def func(sender, words, context):
            print("***", words, sender, context)
            if not words:
                return
            if 'shell' in context:
                self.sender = sender
                self.spawn()
                if words[0].lower()=='ctrl-c':
                    print("sending ctrl-c")
                    self.kill()
                    self.spawn()
                elif words[0].lower()=='exit':
                    self.kill()
                    return Response('Shell has exited.', context=[])
                else:
                    command = ' '.join(words) + '\n'
                    print("sending command", command)
                    self.process.stdin.write(command.encode())
                    self.process.stdin.flush()
                return ''
            else:
                if words[0].lower()=='shell':
                    self.sender = sender
                    return Response("Entering shell...", context=["shell"])
                elif self.process:
                    self.kill()
                    return Response("Shell has exited.", claim=False)

    def spawn(self):
        if not self.process:
            self.process = subprocess.Popen(["bash"], stderr=subprocess.STDOUT, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.thread = threading.Thread(target=self.read_stdout)
            self.thread.start()

    def kill(self):
        if self.process:
            print("killing")
            self.process.kill()
            self.process = None
            self.thread.join()

    def close(self):
        self.kill()
        self.text_visor.close()

    def read_stdout(self):
        while True:
            try:
                text = os.read(self.process.stdout.fileno(), 0x8000).decode()
                if not text:
                    break
            except:
                break
            print("*** text:", text)
            self.text_visor.text_client.text(self.sender, text)
        print("exitting....")

exit = False

def handler(signum, frame):
    global exit
    print("exit")
    exit = True

signal.signal(signal.SIGINT, handler)

shell = Shell()
while not exit:
    time.sleep(1)
shell.close()
