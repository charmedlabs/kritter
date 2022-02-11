#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import sys
import traceback
from termcolor import colored
import threading

def _install_excepthook():
    def _excepthook(type_, value, tb, name=None):
        message = "\nUnhandled exception from " + name + ":\n" if isinstance(name, str) else "\nUnhandled exception:\n"
        message += ''.join(traceback.format_exception(type_, value, tb))
        print(colored(message, "red"))

    sys.excepthook = _excepthook
    sys.unraisablehook = _excepthook
    if sys.version_info.major>=3 and sys.version_info.minor>=8:
        sys.threading = _excepthook

_install_excepthook()


if sys.version_info.major>=3 and sys.version_info.minor<=7:
    def _install_threading_excepthook():
        """
        Workaround for sys.excepthook thread bug
        From
    http://spyced.blogspot.com/2007/06/workaround-for-sysexcepthook-bug.html
       
    (https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470).
        Call once from __main__ before creating any threads.
        If using psyco, call psyco.cannotcompile(threading.Thread.run)
        since this replaces a new-style class method.
        """
        init_old = threading.Thread.__init__
        def init(self, *args, **kwargs):
            init_old(self, *args, **kwargs)
            run_old = self.run
            def run_with_except_hook(*args, **kw):
                try:
                    run_old(*args, **kw)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    sys.excepthook(*sys.exc_info(), self.name)
            self.run = run_with_except_hook
        threading.Thread.__init__ = init


    _install_threading_excepthook()