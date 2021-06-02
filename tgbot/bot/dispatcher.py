import telegram
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler, Updater

from garage_band_bot.settings import TELEGRAM_TOKEN
from logger.log_config import BOT_LOG
from tgbot.bot.handlers import message_handler, post_handler


def setup_dispatcher(dp):
    """Adding handlers for events"""

    dp.add_handler(MessageHandler(Filters.chat_type.private, message_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.channel, post_handler))
    dp.add_handler(CallbackQueryHandler(message_handler))
    BOT_LOG.debug("Event handlers initialized.")


def run_polling():
    """Run in polling mode"""

    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/{bot_info['username']}"

    BOT_LOG.info(f"Polling of '{bot_link}' started")
    updater.start_polling()
    updater.idle()
