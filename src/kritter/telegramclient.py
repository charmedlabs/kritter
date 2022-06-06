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
        self.TOKEN = "5487939010:AAGDFGNneria4_npbFNpj5ONDFDc7Uxnyd8"
        self.application = Application.builder().token(self.token).build()
        self.add_application_handlers()
        self.run_telegram_server(self.application)

    async def run_telegram_server_coroutine(self, application):
        await application.initialize()
        await application.updater.start_polling(
            poll_interval=0.0,
            timeout=10,
            bootstrap_retries=-1,
            read_timeout=2,
            allowed_updates=None,
            drop_pending_updates=None
        )
        asyncio.create_task(application.start())

    def run_telegram_server(self, application):
        loop = asyncio.get_event_loop()
        # this shouldn't block...
        loop.run_until_complete(self.run_telegram_server_coroutine(application))

    def test_telegrambot(self):
        """
        Tests if the bot has been setup correctly
        by the user during the onboarding process
        see telegramdialogue.py in vizy.py
        """
        pass

    def text(self, text):
        """Sends a text to the chat determined by the bot token"""
        pass
    
    def image(self, image) -> None:
        """Sends an image given a file location"""
        pass

    def send(self):
        """Unused by telegram client"""
        pass

    def add_application_handler():
        """
        Adds all handles, mostly commands and message operations,
        to the Application.
        Handlers must be defined above this function
        """
        # MessageHandler(Filters, message_function) --> see 'echobot.py' in python-telegram-bot/examples
        # CommandHandler("command", command_function)
        # self.application.add_handler( CommandHandler(..) or MessageHandler(..) )
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
        """Runs whatever callback_received has been defined to as a coroutine"""
        if self.callback_receive:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.callback_receive, update.effective_message.chat_id, update.message.text)

