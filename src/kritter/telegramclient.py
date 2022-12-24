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
import numpy as np
from telegram.error import TimedOut
from telegram import ForceReply, Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters
import asyncio
# local imports
from .ktextclient import KtextClient, Image, Video

"""
References:
1. Python Telegram Bot | Handlers | https://docs.python-telegram-bot.org/en/stable/telegram.ext.handler.html
2. Ayncio | Coroutines and Tasks | https://docs.python.org/3/library/asyncio-task.html?highlight=run_coroutine_threadsafe#asyncio.run_coroutine_threadsafe
"""

CONFIG_FILE = 'telegram_config.json'
RETRIES = 4
TIMEOUT = 15

class TelegramClient(KtextClient): # Text Messaging Client
    def __init__(self, etcdir, loop=None):
        super().__init__()
        self.task = None
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
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
        self.close()


    def send(self, msg, to):
        if isinstance(msg, str):
            self.text(msg, to)
        elif isinstance(msg, Image):
            self.image(msg.image, to)
        elif isinstance(msg, Video):
            self.video(msg.video, to)            
        elif isinstance(msg, (tuple, list)):
            for m in msg:
                self.send(m, to)
        else:
            raise RuntimeError(f"{type(msg)} is not supported.")

    def text(self, text, to):
        if not self.application:
            print("Telegram doesn't have a token")
            return
        if text:
            text_ = text.strip().lower()
            # Handle URLs
            if text_.startswith("http://") or text_.startswith("https://"):
                # markup can't handle periods -- they need to be escaped
                text = text.replace('.', '\\.') 
            # Print verbatim, fixed font    
            else: 
                text = "```\n"+text+"```"
            for i in range(RETRIES):
                try:
                    asyncio.run_coroutine_threadsafe(self.application.bot.send_message(int(to['id']), text=text, parse_mode="MarkdownV2"), self.loop).result()
                    break
                except TimedOut:
                    print("Timeout. Resending Telegram text...")
                except Exception as e:
                    print("Unable to send text:", e)
    
    def image(self, image, to) -> None:
        """Sends an image given a file location, local or URL; also sending numpy array directly"""
        if not self.application:
            print("Telegram doesn't have a token")
            return
        if isinstance(image, str):
            if os.path.exists(image):
                image = open(image, 'rb') # Telegram bot can take file object
            elif image.lower().startswith("http"):
                pass # We can pass http url's as-is.
            else:
                raise RuntimeError(f"Unknown image type: {image}")
        elif isinstance(image, np.ndarray): 
            try:
                image = cv2.imencode('.jpg', image)[1].tobytes()
            except Exception as e:
                raise RuntimeError(f"Error processing image array: {e}")
        else:
            raise RuntimeError("Unsupported image type")
        # Run send_photo (coroutine)
        for i in range(RETRIES):
            try:
                asyncio.run_coroutine_threadsafe(self.application.bot.send_photo(int(to['id']), image), self.loop).result()
                break
            except TimedOut:
                print("Timeout. Resending Telegram image...")
            except Exception as e:
                print("Unable to send image:", e)

    def video(self, video, to) -> None:
        """Sends a video given a file location, local or URL; also sending numpy array directly"""
        if not self.application:
            print("Telegram doesn't have a token")
            return
        if isinstance(video, str):
            if os.path.exists(video):
                video = open(video, 'rb') # Telegram bot can take file object
            elif video.lower().startswith("http"):
                pass # We can pass http url's as-is.
            else:
                raise RuntimeError(f"Unknown video type: {video}")
        else:
            raise RuntimeError("Unsupported video type")
        # Run send_photo (coroutine)
        for i in range(RETRIES):
            try:
                asyncio.run_coroutine_threadsafe(self.application.bot.send_video(int(to['id']), video), self.loop).result()
                break
            except TimedOut:
                print("Timeout. Resending Telegram video...")
            except Exception as e:
                print("Unable to send video:", e)

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
            sender = {"id": str(update.effective_message.chat.id), "name": update.effective_message.chat.full_name}
            await self.loop.run_in_executor(None, self.receive_callback, update.message.text, sender)

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
            timeout=TIMEOUT,
            bootstrap_retries=-1,
            read_timeout=TIMEOUT,
            allowed_updates=None,
            drop_pending_updates=None
        )
        self.task = asyncio.create_task(self.application.start())

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
        self.close()
        self.application = Application.builder().token(self._config['token']).build() 
        # Command Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv)) 
        # Start server
        for i in range(RETRIES):
            try:
                self.run_coro(self.start_server_coro)
                break
            except TimedOut:
                print("Timeout. Attempting to reconnect to Telegram server...")
            except Exception as e:
                print("Unable to run server:", e)

    def running(self):
        return bool(self.application)

    def close(self):
        try:
            self.run_coro(self.stop_server_coro)
        except:
            pass
