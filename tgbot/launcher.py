import platform

import telegram
from telegram import ParseMode
from telegram.ext import Updater

from garage_band_bot.settings import DEBUG
from logger.log_config import BOT_LOG
from tgbot.bot.dispatcher import setup_dispatcher
from tgbot.models import MessengerBot


def run_polling():
    """Запуск в режиме polling"""
    updaters = []

    for bot in MessengerBot.objects.filter(is_active=True, is_debug=DEBUG).select_related():
        token = bot.telegram_instance.token
        updater = Updater(token, use_context=True)

        dp = updater.dispatcher
        dp = setup_dispatcher(dp)
        dp.bot_data["msg_bot"] = bot

        bot_info = telegram.Bot(token).get_me()
        bot_link = f"https://t.me/{bot_info['username']}"

        BOT_LOG.info(f"Polling of '{bot_link}' started")

        updater.bot.send_message(
            chat_id=bot.telegram_instance.admin_group_id,
            text=f"Бот перезапущен 😉\n<b>{platform.system()} @ {platform.node()}</b>",
            parse_mode=ParseMode.HTML,
        )

        updater.start_polling()
        updaters.append(updater)
    if len(updaters):
        updaters[0].idle()
