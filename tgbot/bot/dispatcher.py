import telegram
from telegram.ext import Updater, Dispatcher, MessageHandler, Filters

from garage_band_bot.settings import TELEGRAM_TOKEN
from tgbot.bot.handlers import message_processor


def setup_dispatcher(dp):
    """Adding handlers for events"""

    dp.add_handler(MessageHandler(Filters.all, message_processor))


def run_pooling():
    """run in pooling mode"""

    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    updater.start_polling()
    updater.idle()