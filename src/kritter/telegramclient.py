from telegram import Update, ForceReply
from telegram.ext import Bot, Application, CommandHandler, MessageHandler, Filters, CallbackContext
import asyncio
# local imports
from ktextclient import KtextClient

"""
TelegramClient is, essentially(?), a wrapper for 
the python-telegram-bot package that will handle
and obscure the asynchronous aspects from the user.
It must be async otherwise Vizy will be blocked, 
incapable of performing its other tasks.
"""

class TelegramClient(KtextClient):
    def __init__(self):
        super().__init__()
        self.callback_receive = None
        self.loop = asyncio.get_event_loop()
        # read /etc/telegram_bot_token.json for bot_token_file
        # hardcoded for now..
        self.bot = Bot("5487939010:AAGDFGNneria4_npbFNpj5ONDFDc7Uxnyd8")
        # self.application = Application()
        # self.TOKEN = "5487939010:AAGDFGNneria4_npbFNpj5ONDFDc7Uxnyd8"

    # async def run_telegram_server_coroutine(self):
    #     await application.initialize()
    #     await application.updater.start_polling(
    #         poll_interval=0.0,
    #         timeout=10,
    #         bootstrap_retries=-1,
    #         read_timeout=2,
    #         allowed_updates=None,
    #         drop_pending_updates=None
    #     )
    #     asyncio.create_task(application.start())

    # def run_telegram_server(application):
    #     loop = asyncio.get_event_loop()
    #     # this shouldn't block...
    #     loop.run_until_complete(run_telegram_server_coro(application))

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
        """"""
        if self.callback_receive:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.callback_receive, update.effective_message.chat_id, update.message.text)

