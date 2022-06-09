from telegram import ForceReply, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters
import asyncio
# local imports
from .ktextclient import KtextClient

"""
TelegramClient is, essentially(?), a wrapper for 
the python-telegram-bot package that will handle
and obscure the asynchronous aspects from the user.
It must be async otherwise Vizy will be blocked, 
incapable of performing its other tasks.
"""

DEFAULT_TYPE = CallbackContext["ExtBot", dict, dict, dict]

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: DEFAULT_TYPE) -> None:
    """Echo the user message."""
    print("****", update)
    print("*****", update.effective_message)
    print("******", update.effective_message.chat_id)
    await update.message.reply_text(update.message.text)

class TelegramClient(KtextClient):
    def __init__(self):
        super().__init__()
        self.callback_receive = None
        self.loop = asyncio.get_event_loop()
        # read /etc/telegram_bot_token.json for bot_token_file
        # hardcoded for now..
        self.TOKEN = "5324425526:AAFX-gW3LOu-gRtpqmRp_deAIdFLMJRVyj8"
        self.application = Application.builder().token(self.TOKEN).build()
        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))

        # on non command i.e message - echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        # self.add_application_handlers()
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

    def add_application_handlers():
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

