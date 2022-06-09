import os 
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
"""

class TelegramClient(KtextClient):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        # read /etc/telegram_bot_token.json for bot_token_file
        # hardcoded for now..
        self.TOKEN = "5324425526:AAFX-gW3LOu-gRtpqmRp_deAIdFLMJRVyj8"
        self.application = Application.builder().token(self.TOKEN).build()
        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))

        # on non command i.e message - echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recv))
        # this shouldn't block...
        self.loop.run_until_complete(self.run_telegram_server())

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
        # Run send_photo (coroutine).  We assume that asyncio loop is already running.
        asyncio.run_coroutine_threadsafe(self.application.bot.send_photo(to, image), self.loop).result()

    def send(self):
        """TelegramClient sends images and texts immediately, so we don't
        need to do anything for send()."""
        pass
    
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

    async def recv(self, update: Update, context: CallbackContext):
        """Runs whatever callback_receive has been defined to as a coroutine"""
        if self.receive_callback:
            # Note, use executor when calling into sync function
            await self.loop.run_in_executor(None, self.receive_callback, update.effective_message.chat_id, update.message.text)

