class KtextClient:
	def __init__(self):
		self.callback_receive = None

	def text(self, to, text):
		pass

	def image(self, to, image):
		pass

	def flush(self):
		pass

    def callback_receive(self):
        def wrap_func(func):
            self.callback_receive = func
        return wrap_func
