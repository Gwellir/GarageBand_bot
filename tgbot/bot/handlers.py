import sys
import traceback

from django.utils.html import escape
from telegram.utils.helpers import mention_html

from garage_band_bot.settings import DEV_TG_ID
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
    """Проверяет, что коллбек принадлежит последнему сообщению из диалога
    и возвращает содержимое, иначе вызывает исключение."""

    if callback_query:
        if last_id and callback_query.message.message_id != last_id:
            raise CallbackExpiredError(callback_query.data, callback_query.from_user.id)
        return callback_query.data
    else:
        return None


# todo make this prepare a file object?
def get_photo_data(message_data, bot):
    """Возвращает данные фотографии из формата данных PTB."""

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
    """
    Обработчик команд администрирования.

    Проверяет, что пользователь, использующий команду, является админом,
    затем исполняет действие, соответствующее команде и ключу.
    Удаляет админ-сообщение.
    """

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

    # todo should only work for destructive actions
    # todo sometimes raises BadRequest
    update.effective_message.delete()


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


def error_handler(update, context):
    # add all the dev user_ids in this list. You can also add ids of channels or groups.
    devs = [DEV_TG_ID]
    try:
        # we want to notify the user of this problem. This will always work, but not notify users if the update is an
        # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
        # could fail
        if update.effective_message:
            text = (
                "Извините, при обработке вашего сообщения произошла непредвиденная ошибка.\n"
                "Уведомление разработчикам отправлено!"
            )
            update.effective_message.reply_text(text)
        # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
        # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
        # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
        # empty string works fine.
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        # lets try to get as much information from the telegram update as possible
        payload = ""
        # normally, we always have an user. If not, its either a channel or a poll update.
        if update.effective_user:
            payload += f" with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}"
        # there are more situations when you don't get a chat
        if update.effective_chat:
            payload += f" within the chat <i>{update.effective_chat.title}</i>"
            if update.effective_chat.username:
                payload += f" (@{update.effective_chat.username})"
        # but only one where you have an empty payload by now: A poll (buuuh)
        if update.poll:
            payload += f" with the poll id {update.poll.id}."
    except AttributeError:
        pass
    # lets put this in a "well" formatted text
    text = (
        f"Hey.\n The error <code>{escape(context.error)}</code> happened{payload}. The full traceback:\n\n<code>{escape(trace)}"
        f"</code>"
    )
    # and send it to the dev(s)
    for dev_id in devs:
        send_message_return_id(text, dev_id, context.bot)
        # context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise
