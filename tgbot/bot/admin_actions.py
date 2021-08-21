"""Содержит логику для администраторских действий."""

from datetime import timedelta

from django.utils.timezone import now
from telegram.error import BadRequest

from tgbot.bot.senders import send_messages_return_ids
from tgbot.exceptions import MessageDoesNotExistError, NoUserWithThisIdError
from tgbot.models import BotUser


# todo organize exception control
def ban_user_by_id(bot, pk, callback=None):
    """Банит пользователя по ID Телеграма, удаляет все сообщения пользователя
    за сутки, отправляет подтверждающее сообщение и ответ на коллбек."""

    try:
        user = BotUser.objects.get(pk=pk)
    except BotUser.DoesNotExist:
        raise NoUserWithThisIdError(pk)
    user.ban()
    Model = bot.get_bound_model()
    user_filter = {
        "user": user,
        "formed_at__gte": now() - timedelta(hours=24),
        "is_complete": True,
    }
    user_requests = Model.objects.filter(**user_filter)
    for request in user_requests.all():
        try:
            delete_channel_message_by_id(bot, request.registered.channel_message_id)
        except MessageDoesNotExistError:
            pass
    msg = {
        "text": f"Пользователь {user} забанен, его посты за последние сутки удалены!"
    }
    callback.answer(msg["text"])
    send_messages_return_ids(msg, bot.telegram_instance.admin_group_id, bot)


def delete_channel_message_by_id(bot, message_id, callback=None):
    """Удаляет сообщение из публикационного канала по id.

    Отправляет уведомление в админскую группу."""

    try:
        Model = bot.get_bound_model()
        bound = Model.objects.get(registered__channel_message_id=message_id)
        bound.delete_post()
    except BadRequest:
        raise MessageDoesNotExistError(message_id)
    if callback:
        msg = {"text": f"Заявка #{bound.registered.pk} удалена!"}
        callback.answer(msg["text"])
        send_messages_return_ids(msg, bot.telegram_instance.admin_group_id, bot)


ADMIN_ACTIONS = {
    "admin_ban": ban_user_by_id,
    "admin_delete": delete_channel_message_by_id,
}
