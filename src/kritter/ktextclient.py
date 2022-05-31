class KtextClient:
    def __init__(self):
        self.callback_receive = None

    def text(self, to, text):
        pass

    def image(self, to, image):
        pass

    def send(self):
        pass

    def callback_receive(self):
        """
        Note, self.callback_receive function is called with two arguments:
        self.callback_receive(from, message) 
        Where from is the user id of the sender, message is the message.  
        """
        def wrap_func(func):
            self.callback_receive = func
        return wrap_func
