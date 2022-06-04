from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# local imports
from ktextclient import KtextClient

class TelegramClient(KtextClient):
    def __init__(self):
        super().__init__()
        self.callback_receive = None

    def text(self, text):
        """Sends a text to the chat determined by the bot token"""
        pass
    
    def image(self, image) -> None:
        """Sends an image given a file location"""
        pass

    def send(self):
        """Unused by telegram client"""
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

    async def handler(self, update: Update, context: CallbackContext):
        """Handler descption ..."""
        if self.callback_receive:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.callback_receive, update.effective_message.chat_id, update.message.text)

