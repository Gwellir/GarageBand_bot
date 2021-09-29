"""Содержит функции отправки сообщений в telegram."""

from telegram import ParseMode
from telegram.error import BadRequest, ChatMigrated, Unauthorized

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.utils import build_inline_button_markup, build_reply_button_markup


def send_messages_return_ids(message_data, user_id, msg_bot, reply_to=None):
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
    bot = msg_bot.telegram_instance.tg_bot
    ids = []
    try:
        if "caption" in message_data.keys():
            if "photo" in message_data.keys():
                msg = bot.send_photo(
                    caption=message_data["caption"],
                    photo=message_data["photo"],
                    **params_dict,
                ).result()
            elif "video" in message_data.keys():
                msg = bot.send_video(
                    caption=message_data["caption"],
                    video=message_data["video"],
                    **params_dict,
                )
            ids = [msg.message_id]

        else:
            msg = bot.send_message(
                text=message_data["text"], disable_web_page_preview=True, **params_dict
            ).result()
            ids = [msg.message_id]
    except (BadRequest, ChatMigrated, Unauthorized) as e:
        BOT_LOG.warning(f"Could not reach {user_id} due to {e.args}")

    # todo change to queue implementation
    return ids
