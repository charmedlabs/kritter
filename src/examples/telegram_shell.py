import time
from kritter.ktextvisor import KtextVisor, KtextVisorTable, Response
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

        def ctrl_c(words, sender, context):
            self.kill()
            self.spawn()
            return "^C"

        def exit(words, sender, context):
            self.kill()
            return Response('Shell has exited.', context=[])

        def command(words, sender, context):
            command = ' '.join(words) + '\n'
            print("sending command", command)
            self.process.stdin.write(command.encode())
            self.process.stdin.flush()
            return Response("") # Empty response, but claim=True

        def shell(words, sender, context):
            self.sender = sender
            return Response("Entering shell...", context=["shell"])

        def shell_other(words, sender, context):
            if self.process:
                self.kill()
                return Response("Shell has exited.", claim=False)

        tv_shell_table = KtextVisorTable({
            "ctrl-c": (ctrl_c, "Interrupts current program."),
            "exit": (exit, "Exits shell."),
            "*": (command, "Any shell command.")
        }, help_claim=True) # help_claim basically says that we're claiming all commands
        tv_table = KtextVisorTable({
            "shell": (shell, "Starts shell."),
            "*": (shell_other, None)
        })

        @self.text_visor.callback_receive(True)
        def func(words, sender, context):
            print("***", words, sender, context)
            if 'shell' in context:
                self.sender = sender
                self.spawn()
                return tv_shell_table.lookup(words, sender, context)
            else:
                return tv_table.lookup(words, sender, context)

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
            self.text_visor.send(text, self.sender)
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
