#
# This file is part of Vizy 
#
# All Vizy source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Vizy source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os
import json
import cv2
from telegram import ForceReply, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters
import asyncio
# local imports
from .ktextclient import KtextClient

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
CONFIG_FILE = 'telegram_config.json'


class TelegramClient(KtextClient): # Text Messaging Client
    def __init__(self, etcdir):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.config_filename = os.path.join(etcdir, CONFIG_FILE) 
        self.application = None 
        self.read_config()
        self.run_server()

    def read_config(self):
        try:
            with open(self.config_filename, "r") as file:
                self._config = json.load(file)
        except:
            self._config = {}
            self._config['token'] = None

    def write_config(self):
        try:
            with open(self.config_filename, "w") as file:
                json.dump(self._config, file)
        except Exception as e:
            print(f"Unable to write Telegram config file {self.config_filename}: {e}")

    def set_token(self, token):
        self._config['token'] = token
        self.write_config()
        self.run_server()

    def remove_token(self):
        self._config['token'] = None
        self.write_config()
        self.run_coro(self.stop_server_coro)

    def text(self, to, text):
        if not self.application:
            raise RuntimeError("Telegram doesn't have a token")
        """Sends a text to the chat determined by the bot token"""
        asyncio.run_coroutine_threadsafe(self.application.bot.send_message(to, text="```\n"+text+"\n```", parse_mode="MarkdownV2"), self.loop).result()
    
    def image(self, to, image) -> None:
        if not self.application:
            raise RuntimeError("Telegram doesn't have a token")
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
        except Exception as e:
            print(f'The send photo coroutine raised an exception: {e}')

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
        # note: commands do not display with new lines..
        newline = '\n'
        await update.message.reply_text(newline.join(
            f"Help!"
            f"Commands : help, start"
            f"Other : recv -> user defined callback"
        ))

    async def recv(self, update: Update, context: CallbackContext):
        """Wrap callback_receive as a coroutine and submit to run"""
        if self.receive_callback:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.receive_callback, update.effective_message.chat_id, update.message.text)

    async def stop_server_coro(self):
        if self.application:
            await self.application.updater.stop()
            await self.application.updater.shutdown()
            await self.application.stop()
            self.application = None

    async def start_server_coro(self):
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

    def run_coro(self, coro):
        # Two cases: asyncio event loop is running
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro(), self.loop).result()
        # ... or hasn't started to run yet.
        else:
            self.loop.run_until_complete(coro()) 

    def run_server(self):
        # If we don't have a token, no sense in running server. 
        if self._config['token'] is None:
            return
        # We need to set the event loop to the main event loop, otherwise if we're run from 
        # another thread, the asyncio code in Telegram will complain that there's no event 
        # loop in the current thread.  
        asyncio.set_event_loop(self.loop)
        # Clean up server (if needed)
        self.run_coro(self.stop_server_coro)
        self.application = Application.builder().token(self._config['token']).build() 
        # Command Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv)) 
        # Start server
        self.run_coro(self.start_server_coro)

    def running(self):
        return bool(self.application)