from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.dialog import DialogProcessor
from tgbot.bot.senders import send_telegram_message_return_id
from tgbot.bot.utils import extract_user_data_from_update
from tgbot.exceptions import CallbackExpiredError
from tgbot.models import Dialog


def get_and_verify_callback_data(callback_query, last_id):
    if callback_query:
        if last_id and callback_query.message.message_id != last_id:
            raise CallbackExpiredError(callback_query.data, callback_query.from_user.id)
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
    last_id = context.user_data.get("last_message_id", None)
    try:
        command = get_and_verify_callback_data(update.callback_query, last_id)
        if command:
            update.callback_query.answer()
    except CallbackExpiredError as e:
        BOT_LOG.warning(
            LogStrings.DIALOG_INPUT_ERROR.format(
                user_id=update.effective_user.username,
                stage=None,
                args=e.args,
            )
        )
        update.callback_query.answer("Используйте кнопки из последнего сообщения!")
        return

    # todo привести к неспецифическому для телеграма виде
    input_data = {
        "bot": context.bot,
        "text": msg.text,
        "caption": msg.caption,
        "photo": get_photo_data(msg, context.bot),
        "callback": command,
    }
    dialog_processor = DialogProcessor(dialog, input_data)
    replies = dialog_processor.process()

    for reply in replies:
        context.user_data["last_message_id"] = send_telegram_message_return_id(
            reply, update.effective_user, context.bot
        )
