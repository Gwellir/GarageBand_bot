from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.dialog import DialogProcessor
from tgbot.bot.senders import send_telegram_message
from tgbot.bot.utils import extract_user_data_from_update
from tgbot.models import Dialog


def get_callback_data(callback_query):
    if callback_query:
        return callback_query.data
    else:
        return None


# todo make this prepare a file object?
def get_photo_data(message_data, bot):
    if message_data.photo:
        return message_data.photo[-1].file_id
    else:
        return None


def post_handler(update, context):
    """
    Обработчик для сообщений каналов

    Требуется для отслеживания ID каналов.
    """

    BOT_LOG.info(
        LogStrings.CHANNEL_POST.format(
            channel_id=update.channel_post.chat_id,
        )
    )


def message_handler(update, context):
    """Обработчик для всех получаемых сообщений.

    Передаёт информацию о событии соответствующему инстансу DialogProcessor"""

    # todo добавить привязку инстансов DialogProcessor к пользователям
    user_data = extract_user_data_from_update(update)
    dialog = Dialog.get_or_create(user_data)
    msg = update.effective_message
    callback = get_callback_data(update.callback_query)
    # todo привести к неспецифическому для телеграма виде
    input_data = {
        "bot": context.bot,
        "text": msg.text,
        "caption": msg.caption,
        "photo": get_photo_data(msg, context.bot),
        "callback": callback,
    }
    dialog_processor = DialogProcessor(dialog, input_data)
    replies = dialog_processor.process()

    for reply in replies:
        send_telegram_message(reply, update.effective_user, context.bot)

    # after processing
    if callback:
        update.callback_query.answer()
