"""Содержит функции отправки сообщений в telegram."""
from telegram import Bot, ParseMode

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.utils import build_inline_button_markup, build_reply_button_markup


def send_message_return_id(message_data, user_id, msg_bot, reply_to=None):
    """Отправляет сообщение через телеграм бота.

    Формирует структуру кнопок, определяет, требуется ли отправка обычного сообщения,
    либо же фотографии с описанием.
    Возвращает message_id сообщения в соответствующем чате TG.
    """

    BOT_LOG.debug(
        LogStrings.DIALOG_SEND_MESSAGE.format(
            user_id=user_id,
            reply=message_data,
        )
    )
    markup = None
    if "buttons" in message_data.keys():
        markup = build_inline_button_markup(message_data["buttons"])
    elif "text_buttons" in message_data.keys():
        markup = build_reply_button_markup(message_data["text_buttons"])
    params_dict = dict(
        chat_id=user_id,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=reply_to,
    )
    # todo wrap in TRY EXCEPT (ChatMigrated, ...)
    bot = Bot(msg_bot.telegram_instance.token)
    if "caption" in message_data.keys():
        msg = bot.send_photo(
            caption=message_data["caption"], photo=message_data["photo"], **params_dict
        )
    else:
        msg = bot.send_message(
            text=message_data["text"], disable_web_page_preview=True, **params_dict
        )

    return msg.message_id
