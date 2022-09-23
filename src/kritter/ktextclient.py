#
# This file is part of Vizy 
#
# All Vizy source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Vizy source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#
from collections import UserString

class Image:
    def __init__(self, image):
        self.image = image

class Video:
    def __init__(self, video):
        self.video = video

class KtextClient:
    def __init__(self):
        self.receive_callback = None

    def send(self, msg, to):
        pass

    def callback_receive(self):
        """
        Note, self.callback_receive function is called with two arguments:
        self.callback_receive(message, from) 
        Where from is the user id of the sender, message is the message.  
        """
        def wrap_func(func):
            self.receive_callback = func
        return wrap_func

