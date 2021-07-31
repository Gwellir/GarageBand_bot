"""Содержит функции запуска и настройки telegram-бота."""

from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler

from logger.log_config import BOT_LOG
from tgbot.bot.handlers import (
    admin_command_handler,
    chat_ban_user,
    error_handler,
    message_handler,
    post_handler,
    show_user_requests_stats,
)


def setup_dispatcher(dp):
    """Создаёт обработчики для приходящих от Telegram событий."""

    dp.add_handler(CallbackQueryHandler(admin_command_handler, pattern=r"^admin_.*"))
    dp.add_handler(CommandHandler(["ban"], chat_ban_user))
    dp.add_handler(CommandHandler(["user_request_stats"], show_user_requests_stats))
    dp.add_handler(MessageHandler(Filters.chat_type.private, message_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.channel, post_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.groups, post_handler))
    dp.add_handler(CallbackQueryHandler(message_handler))
    dp.add_error_handler(error_handler)

    BOT_LOG.debug("Event handlers initialized.")

    return dp
