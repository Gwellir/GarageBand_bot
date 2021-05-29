from telegram import ParseMode

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import PUBLISHING_CHANNEL_ID
from tgbot.bot.utils import build_button_markup


def send_telegram_message(message_data, user, bot):
    BOT_LOG.debug(
        LogStrings.DIALOG_SEND_MESSAGE.format(
            user_id=user.username,
            reply=message_data,
        )
    )
    markup = None
    if "buttons" in message_data.keys():
        markup = build_button_markup(message_data["buttons"])
    params_dict = dict(
        chat_id=user.id,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN,
    )
    if "caption" in message_data.keys():
        bot.send_photo(
            caption=message_data["caption"], photo=message_data["photo"], **params_dict
        )
    else:
        bot.send_message(text=message_data["text"], **params_dict)


def publish_summary(summary, user, bot):
    BOT_LOG.debug(
        LogStrings.DIALOG_PUBLISH_REQUEST.format(
            user_id=user.username,
            channel_id=PUBLISHING_CHANNEL_ID,
            summary=summary,
        )
    )
    bot.send_photo(
        caption=summary["caption"],
        photo=summary["photo"],
        chat_id=PUBLISHING_CHANNEL_ID,
        parse_mode=ParseMode.MARKDOWN,
    )
