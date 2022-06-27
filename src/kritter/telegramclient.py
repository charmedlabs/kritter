import os
from tokenize import Token 
import cv2
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

Active Questions:
1. Abilty to add Multiple Bots --> dynamic command handling in dialog ?
"""

"""
References:
1. Python Telegram Bot | Handlers | https://docs.python-telegram-bot.org/en/stable/telegram.ext.handler.html
2. Ayncio | Coroutines and Tasks | https://docs.python.org/3/library/asyncio-task.html?highlight=run_coroutine_threadsafe#asyncio.run_coroutine_threadsafe
"""

dev_tokens = {
    'matt': "5487939010:AAGDFGNneria4_npbFNpj5ONDFDc7Uxnyd8",
    'other': ""
}

DEFAULT_TIMEOUT = 60 * 5 # seconds; five minute timeout
TOKEN_FILE = 'telegram_token.json'
TOKEN_ERR = 3

class TelegramClient(KtextClient): # Text Messaging Client
    def __init__(self, etcdir):
        super().__init__()
        # todo: client controlling start/stop of Application
        # -- new loop each 'start' attempt ? 
        self.loop = asyncio.get_event_loop()
        self.token_file = os.path.join(etcdir, TOKEN_FILE) 
        self.update() 

    def take_action(self):
        '''Run the state of the bot'''
        try:
            # ? handle self.token_error ? 
            # self.start_bot() if self.token else self.stop_bot()
            if self.token: # has token, is active
                self.start_bot()
            else:
                self.stop_bot()
        except Exception as exc:
            pass

    def update(self):
        """Update token and start bot"""
        try:
            # create file if not exists, overwrite contexts
            self.token = None
            with open(self.token_file, 'r') as file:
                token = file.read()
                if len(token) > 0 : 
                    self.token = token
        except: 
            # ? set self.token_error to exception
            pass
        self.take_action()

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

    def remove_token(self):
        '''Empty contents of token file'''
        try:
            # if os.path.exists(self.token_file):
            #     os.remove(self.token_file)
            #     self.update()
            with open(self.token_file, 'w') as file:
                file.truncate(0) # remove all contents
                self.update()
        except Exception as exc:
            print(f'TelegramClient Remove Token encountered an error: {exc!r}')

    def text(self, to, text):
        """Sends a text to the chat determined by the bot token"""
        asyncio.run_coroutine_threadsafe(self.application.bot.send_message(to, text=text), self.loop).result()
    
    def image(self, to, image) -> None:
        """Sends an image given a file location, local or URL; also sending numpy array directly"""
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
        future = asyncio.run_coroutine_threadsafe(self.application.bot.send_photo(to, image), self.loop)
        try:
            result = future.result(DEFAULT_TIMEOUT)
        # todo: get TimoutError working
        # except concurrent.futures.TimeoutError:
        #     print('The coroutine took too long, cancelling the task...')
        #     future.cancel()
        except Exception as exc:
            print(f'The coroutine raised an exception: {exc!r}')
        else:
            # todo: log result --> ? self.token_error ? 
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
        """Replies with small list of commands and functions """
        newline = '\n'
        await update.message.reply_text(newline.join(
            f"Help!"
            f"Commands : help, start"
            f"Other : recv -> user defined callback"
        ))

    async def echo(update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        await update.message.reply_text(update.message.text)

    async def recv(self, update: Update, context: CallbackContext):
        """Runs whatever callback_receive has been defined to as a coroutine"""
        if self.receive_callback:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.receive_callback, update.effective_message.chat_id, update.message.text)

    def setup_handlers(self):
        """Adds the above handlers to the class Telegram application"""
        # Command Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        # Non Command Handlers - so far only messages -- todo: answer: any other 'non commands' ?
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)) # echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv)) # echo the message on Telegram

    def stop_bot(self):
        '''Stops bot if one is running, control event loop too? '''
        try:
            self.application = None
            # if self.application:
            #     self.application.stop()
        except Exception as exc:
            print(f'Stop Bot encountered an exception {exc!r}')
        print(f'shutdown hit')

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

    def start_bot(self):
        try:
            self.application = Application.builder().token(self.token).build() # todo: link to 'builder' & 'build'
            self.setup_handlers()
            self.loop.run_until_complete(self.run_telegram_server()) # this shouldn't block... runs application server ansychronousely
        except Exception as exc:
            print(f'Exception occured starting bot {exc!r}')
            # set self.token_error to exception --> output to dialog
            # ? self.take_action() --> handle self.token_error based ?
            pass
