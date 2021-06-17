"""Содержит функции запуска и настройки telegram-бота."""

import telegram
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from garage_band_bot.settings import ADMIN_GROUP_ID, TELEGRAM_TOKEN
from logger.log_config import BOT_LOG
from tgbot.bot.handlers import (
    admin_command_handler,
    chat_ban_user,
    error_handler,
    message_handler,
    post_handler,
)


def setup_dispatcher(dp):
    """Создаёт обработчики для приходящих от Telegram событий."""

    dp.add_handler(CallbackQueryHandler(admin_command_handler, pattern=r"^admin_.*"))
    dp.add_handler(CommandHandler(["ban"], chat_ban_user))
    dp.add_handler(MessageHandler(Filters.chat_type.private, message_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.channel, post_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.groups, post_handler))
    dp.add_handler(CallbackQueryHandler(message_handler))
    dp.add_error_handler(error_handler)

    BOT_LOG.debug("Event handlers initialized.")


def run_polling():
    """Запуск в режиме polling"""

    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/{bot_info['username']}"

    BOT_LOG.info(f"Polling of '{bot_link}' started")

    updater.bot.send_message(chat_id=ADMIN_GROUP_ID, text="Бот перезапущен 😉")

    updater.start_polling()
    updater.idle()
