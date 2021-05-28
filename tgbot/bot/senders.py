from telegram import ParseMode

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import PUBLISHING_CHANNEL_ID
from tgbot.bot.utils import build_button_markup


def send_telegram_messages(message_data, user, bot):
    for reply in message_data:
        BOT_LOG.debug(
            LogStrings.DIALOG_SEND_MESSAGE.format(
                user_id=user.username,
                reply=reply,
            )
        )
        markup = None
        if "buttons" in reply.keys():
            markup = build_button_markup(reply["buttons"])
        params_dict = dict(
            chat_id=user.id,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
        if "caption" in reply.keys():
            bot.send_photo(
                caption=reply["caption"], photo=reply["photo"], **params_dict
            )
        else:
            bot.send_message(text=reply["text"], **params_dict)


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
