from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.admin_actions import ADMIN_ACTIONS
from tgbot.bot.dialog import DialogProcessor
from tgbot.bot.senders import send_message_return_id
from tgbot.bot.utils import extract_user_data_from_update
from tgbot.exceptions import (
    AdminActionError,
    CallbackExpiredError,
    UnknownAdminCommandError,
    UserIsBannedError,
)
from tgbot.models import BotUser, Dialog


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
    Обработчик для сообщений каналов и групп

    Требуется для отслеживания ID каналов и групп.
    """

    BOT_LOG.info(
        LogStrings.CHANNEL_POST.format(
            channel_id=update.effective_message.chat_id,
        )
    )


def admin_command_handler(update, context):
    user = extract_user_data_from_update(update)
    try:
        BotUser.objects.get(user_id=user["user_id"], is_staff=True)
    except BotUser.DoesNotExist:
        # todo unify callback and exception processing
        update.callback_query.answer("Ваш аккаунт не является администратором!")
        return

    command, key = update.callback_query.data.split()

    try:
        action = ADMIN_ACTIONS[command]
    except KeyError:
        raise UnknownAdminCommandError(command, key)

    try:
        action(context.bot, int(key), callback=update.callback_query)
    except (AdminActionError, UserIsBannedError) as e:
        update.callback_query.answer(e.args[0])


def message_handler(update, context):
    """Обработчик для всех получаемых сообщений.

    Передаёт информацию о событии соответствующему инстансу DialogProcessor"""

    # todo добавить привязку инстансов DialogProcessor к пользователям
    user_data = extract_user_data_from_update(update)
    try:
        dialog = Dialog.get_or_create(user_data)
    except UserIsBannedError as e:
        BOT_LOG.warning(
            LogStrings.DIALOG_INPUT_ERROR.format(
                user_id=update.effective_user.username,
                stage=None,
                args=e.args[0],
            )
        )
        return
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
        context.user_data["last_message_id"] = send_message_return_id(
            reply, update.effective_user.id, context.bot
        )
