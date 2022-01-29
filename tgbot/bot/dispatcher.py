"""Содержит функции запуска и настройки telegram-бота."""
from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, Dispatcher, Filters, MessageHandler

from logger.log_config import BOT_LOG
from tgbot.bot import handlers


def process_telegram_event(update_json, dp):
    update = Update.de_json(update_json, dp.bot)
    dp.update_queue.put(update)


def setup_dispatcher(dp: Dispatcher) -> Dispatcher:
    """Создаёт обработчики для приходящих от Telegram событий."""

    dp.add_handler(
        CallbackQueryHandler(handlers.admin_command_handler, pattern=r"^admin_.*")
    )
    dp.add_handler(CommandHandler(["ban"], handlers.chat_ban_user))
    dp.add_handler(
        CommandHandler(["user_request_stats"], handlers.show_user_requests_stats)
    )
    dp.add_handler(
        MessageHandler(
            Filters.regex("/post_ad\n.*") | Filters.caption_regex("/post_ad\n.*"),
            handlers.post_ad,
        )
    )
    dp.add_handler(MessageHandler(Filters.chat_type.private, handlers.message_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.channel, handlers.post_handler))
    dp.add_handler(MessageHandler(Filters.chat_type.groups, handlers.post_handler))
    dp.add_handler(CallbackQueryHandler(handlers.message_handler))
    dp.add_error_handler(handlers.error_handler)

    BOT_LOG.debug("Event handlers initialized.")

    return dp
