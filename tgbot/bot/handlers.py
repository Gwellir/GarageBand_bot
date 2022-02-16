import re
import sys
import traceback
from datetime import datetime, timedelta
from time import sleep

from django.utils.html import escape
from django.utils.timezone import now
from telegram import ChatPermissions
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html

from convoapp.dialog_state_machine import DialogStateMachine
from convoapp.models import Message
from garage_band_bot.settings import DEV_TG_ID
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot import exceptions
from tgbot.bot.admin_actions import ADMIN_ACTIONS
from tgbot.bot.senders import send_messages_return_ids
from tgbot.bot.utils import extract_user_data_from_update, get_bot_message_as_text
from tgbot.models import BotUser


def get_text_from_inline_keyboard(keyboard, data):
    for row in keyboard:
        for button in row:
            if button.callback_data == data:
                return button.text
    return None


def get_and_verify_callback_data(callback_query, last_id):
    """Проверяет, что коллбек не пуст, и возвращает содержимое, иначе None"""

    if callback_query:
        if callback_query.data and (
            last_id is None or callback_query.message.message_id == last_id
        ):
            try:
                callback_query.answer()
                button_text = get_text_from_inline_keyboard(
                    callback_query.message.reply_markup.inline_keyboard,
                    callback_query.data,
                )
                return callback_query.data, button_text
            except BadRequest:
                pass
        elif callback_query.message.message_id != last_id:
            callback_query.answer("Вы нажали на кнопку в старом сообщении!")
            raise exceptions.CallbackExpiredError(callback_query.data)
    else:
        return None, None


# todo make this prepare a file object?
def get_photo_data(message_data):
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

    # для работы отзовика нам требуется номер поста из канала в группе
    if update.edited_message:
        return
    msg_bot = context.bot_data.get("msg_bot")
    publish_id = msg_bot.telegram_instance.publish_id
    fwd_msg_id = update.effective_message.forward_from_message_id
    fwd_from_chat = update.effective_message.forward_from_chat
    if fwd_msg_id and fwd_from_chat and fwd_from_chat.id == publish_id:
        model = msg_bot.get_bound_model()
        try:
            object_ = model.objects.get(
                registered_posts__channel_message_id=fwd_msg_id,
                registered_posts__created_at__gte=now() - timedelta(minutes=5),
                registered_posts__is_deleted=False,
            )
            post_object = object_.registered
            post_object.group_message_id = update.effective_message.message_id
            post_object.save()

            if msg_bot.get_bound_name() == "salead":
                object_.post_media()

        except model.DoesNotExist:
            pass

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
        raise exceptions.UnknownAdminCommandError(command, key)

    bot = context.bot_data.get("msg_bot")
    try:
        action(bot, int(key), callback=update.callback_query)
    except (exceptions.AdminActionError, exceptions.UserIsBannedError) as e:
        update.callback_query.answer(e.args[0])

    # todo should only work for destructive actions
    # todo sometimes raises BadRequest
    update.effective_message.delete()


def show_user_requests_stats(update, context):

    bot = context.bot_data.get("msg_bot")
    # todo optimize db request
    length = 30
    users = BotUser.objects.all().order_by("pk")
    text = ""
    i = 0
    for user in users:
        stats = user.stats_as_tg_html()
        if stats:
            text = f"{text}{user.stats_as_tg_html()}\n"
            i += 1
        if i == length - 1:
            send_messages_return_ids(
                {"text": text}, bot.telegram_instance.admin_group_id, bot
            )
            sleep(0.5)
            i = 0
            text = ""
    if text:
        send_messages_return_ids(
            {"text": text}, bot.telegram_instance.admin_group_id, bot
        )


def post_ad(update, context):
    """Создаёт и размещает в канале рекламное сообщение."""

    user = extract_user_data_from_update(update)
    try:
        BotUser.objects.get(user_id=user["user_id"], is_staff=True)
    except BotUser.DoesNotExist:
        # todo unify callback and exception processing
        return

    msg = update.effective_message
    if msg.text:
        _, btn_name, btn_link, post_text = msg.text.split("\n", 3)
    elif msg.caption:
        _, btn_name, btn_link, post_text = msg.caption.split("\n", 3)
    msg_data = {
        "text": post_text,
        "buttons": [
            [
                {
                    "text": btn_name,
                    "url": btn_link,
                },
            ]
        ],
    }
    if msg.caption:
        msg_data["caption"] = msg_data.pop("text")
        if msg.photo:
            msg_data["photo"] = msg.photo[-1]
        elif msg.video:
            msg_data["video"] = msg.video
    bot = context.bot_data.get("msg_bot")
    send_messages_return_ids(msg_data, bot.telegram_instance.publish_id, bot)


def chat_ban_user(update, context):
    """Банит пользователя в чате по ответу на его сообщение."""

    user = extract_user_data_from_update(update)
    try:
        BotUser.objects.get(user_id=user["user_id"], is_staff=True)
    except BotUser.DoesNotExist:
        # todo unify callback and exception processing
        return

    reply = update.effective_message.reply_to_message
    if not reply:
        return
    uid, nick = (
        reply.from_user.id,
        reply.from_user.username
        if reply.from_user.username
        else reply.from_user.full_name,
    )
    bot = context.bot_data.get("msg_bot")
    try:
        context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            until_date=datetime.now() + timedelta(hours=24),
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            ),
        )
        send_messages_return_ids(
            {"text": f"Пользователь {nick} {uid} забанен в обсуждении на сутки"},
            update.effective_chat.id,
            bot,
        )
        reply.delete()
    except BadRequest:
        update.effective_message.reply_text("Невозможно забанить владельца группы!")
        return


def message_handler(update, context):
    """Обработчик для всех получаемых сообщений.

    Передаёт информацию о событии соответствующему инстансу DialogProcessor"""

    # todo добавить привязку инстансов DialogProcessor к пользователям

    try:
        user_data = extract_user_data_from_update(update)
        BOT_LOG.info(LogStrings.USER_DATA_FROM_UPDATE.format(user_data=user_data))
    # todo think how to use edits?
    except exceptions.MessageIsAnEditError as e:
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
        command, button_text = get_and_verify_callback_data(
            update.callback_query, last_id
        )
    except exceptions.CallbackExpiredError:
        return

    # todo привести к неспецифическому для телеграма виде
    bot = context.bot_data.get("msg_bot")
    input_data = {
        "bot": bot,
        "id": msg.message_id,
        "text": msg.text if not command else button_text,
        "caption": msg.caption,
        "photo": get_photo_data(msg),
        "callback": command,
        "query": update.callback_query if command else None,
        "media_group_id": msg.media_group_id,
    }

    try:
        dialog_processor = DialogStateMachine(user_data, input_data)
        replies = dialog_processor.process()
    except exceptions.UserIsBannedError as e:
        BOT_LOG.warning(
            LogStrings.DIALOG_INPUT_ERROR.format(
                user_id=user_data.get("username"),
                stage=None,
                args=e.args[0],
            )
        )
        return
    except exceptions.ActionAlreadyCompletedError as e:
        BOT_LOG.warning(
            LogStrings.DIALOG_INPUT_ERROR.format(
                user_id=user_data.get("username"),
                stage=None,
                args=e.args[0],
            )
        )
        # update.callback_query.answer("Это действие уже совершено!")
        return

    for reply in replies:
        ids = send_messages_return_ids(reply, update.effective_user.id, bot)
        Message.objects.create(
            dialog=dialog_processor.dialog,
            stage=dialog_processor.dialog.bound.stage_id,
            message_id=ids[0],
            text=get_bot_message_as_text(reply),
            is_incoming=False,
        )
    if replies:
        context.user_data["last_message_id"] = ids[-1]


def error_handler(update, context):
    devs = [DEV_TG_ID]
    try:
        # if update.effective_message:
        #     text = (
        #         "Извините, при обработке вашего сообщения"
        #         " произошла непредвиденная ошибка.\n"
        #         "Попробуйте повторить через несколько минут.\n"
        #         "Уведомление разработчикам отправлено!"
        #     )
        # update.effective_message.reply_text(text)
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        payload = ""
        if update.effective_user:
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name
            payload += f" with the user {mention_html(user_id, user_name)}"
        if update.effective_chat:
            payload += f" within the chat <i>{update.effective_chat.title}</i>"
            if update.effective_chat.username:
                payload += f" (@{update.effective_chat.username})"
        if update.poll:
            payload += f" with the poll id {update.poll.id}."
    except AttributeError:
        pass
    text = (
        f"Hey.\n The error <code>{escape(context.error)}</code> happened{payload}."
        f" The full traceback:\n\n<code>{escape(trace)}"
        f"</code>"
    )
    bot = context.bot_data.get("msg_bot")
    if len(text) > 4000:
        text = re.sub(r"^.*/venv/.*$", "", text, flags=re.MULTILINE)
    if len(text) > 4000:
        text = f"{text[:3000]}\n\n...\n\n{text[-1000:]}"
    for dev_id in devs:
        send_messages_return_ids({"text": text}, dev_id, bot)
    raise
