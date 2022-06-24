import os
from tokenize import Token 
import cv2
from telegram import ForceReply, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters
import asyncio
# local imports
from .ktextclient import KtextClient

DEFAULT_TIMEOUT = 300 # five minute timeout

"""
TelegramClient is, essentially(?), a wrapper for 
the python-telegram-bot package that will handle
and obscure the asynchronous aspects from the user.
It must be async otherwise Vizy will be blocked, 
incapable of performing its other tasks.

Active Questions:
1. Abilty to add Multiple Bots --> dynamic command handling in dialog ?
"""

"""
References:
1. Python Telegram Bot | Handlers | https://docs.python-telegram-bot.org/en/stable/telegram.ext.handler.html
2. Ayncio | Coroutines and Tasks | https://docs.python.org/3/library/asyncio-task.html?highlight=run_coroutine_threadsafe#asyncio.run_coroutine_threadsafe
"""

dev_tokens = {
    'matt': "5324425526:AAFX-gW3LOu-gRtpqmRp_deAIdFLMJRVyj8",
    'rich': "",
    'other': ""
}

TOKEN_FILE = 'telegram_token.json'

class TelegramClient(KtextClient): # Text Messaging Client
    def __init__(self, etcdir):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.token_file = os.path.join(etcdir, TOKEN_FILE) 
        self.token = None
        self.set_token(dev_tokens['matt']) 
        self.application = Application.builder().token(self.token).build() # todo: link to 'builder' & 'build'
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        ## Test handlers in init..
        # Non Command Handlers - so far only messages -- todo: answer: any other 'non commands' ?
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)) # echo the message on Telegram
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv)) # echo the message on Telegram
        # self.setup_handlers() # add all handlers (commands, non-commands, etc..) 
        self.loop.run_until_complete(self.run_telegram_server()) # this shouldn't block... runs application server ansychronousely
    
    async def run_telegram_server(self):
        await self.application.initialize()
        await self.application.updater.start_polling(
            poll_interval=0.0,
            timeout=10,
            bootstrap_retries=-1,
            read_timeout=2,
            allowed_updates=None,
            drop_pending_updates=None
        )
        asyncio.create_task(self.application.start())

    def update(self):
        """Update token and state"""
        try:
            # create file if not exists, overwrite contexts
            with open(self.token_file, 'r') as file:
                token = file.read()
                if len(token) > 0 : 
                    self.token = token
        except: 
            pass        

    def set_token(self, token):
        try:
            # create file if not exists, overwrite contexts
            with open(self.token_file, 'w+') as file:
                # json.load(file)
                file.write(token)
                file.read() # self.update does not read from file without this line, perhaps a timer is needed ?
                self.update()
        except: 
            pass

    # 
    def test_telegrambot(self):
        """
        Tests if the bot has been setup correctly
        by the user during the onboarding process
        see telegramdialogue.py in vizy.py
        """
        pass

    def text(self, to, text):
        """Sends a text to the chat determined by the bot token"""
        asyncio.run_coroutine_threadsafe(self.application.bot.send_message(to, text=text), self.loop).result()
    
    def image(self, to, image) -> None:
        """Sends an image given a file location"""
        if isinstance(image, str):
            if os.path.exists(image):
                with open(image, 'rb') as image:
                    image = image.read()
            elif image.lower().startswith("http"):
                pass # We can pass http url's as-is.
            else:
                raise RuntimeError(f"Unknown image type: {image}")
        else: # assume it's a numpy array
            try:
                image = cv2.imencode('.jpg', image)[1].tobytes()
            except Exception as e:
                raise RuntimeError(f"Error processing image array: {e}")
        # Run send_photo (coroutine)
        # Submit the coroutine to class's running loop
        future = asyncio.run_coroutine_threadsafe(self.application.bot.send_photo(to, image), self.loop).result()
        try:
            result = future.result(DEFAULT_TIMEOUT)
        # todo: get TimoutError working
        # except concurrent.futures.TimeoutError:
        #     print('The coroutine took too long, cancelling the task...')
        #     future.cancel()
        except Exception as exc:
            print(f'The coroutine raised an exception: {exc!r}')
        else:
            # todo: log result
            pass

    # Commands
    async def start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    async def help(self, update: Update, context: CallbackContext):
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    async def echo(update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        await update.message.reply_text(update.message.text)

    async def recv(self, update: Update, context: CallbackContext):
        """Runs whatever callback_receive has been defined to as a coroutine"""
        if self.receive_callback:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.receive_callback, update.effective_message.chat_id, update.message.text)

    def setup_handlers(self):
        """Adds the above handlers to the class Telegram application
        todo: make a single fucntion so no handler is ever forgotten ? --> onboarding, ease-of-use, difficulty of implementation ?
        """
        # Command Handlers
        # self.application.add_handler(CommandHandler("start", self.start))
        # self.application.add_handler(CommandHandler("help", self.help))
        # # Non Command Handlers - so far only messages -- todo: answer: any other 'non commands' ?
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)) # echo the message on Telegram
        # # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv)) # echo the message on Telegram

