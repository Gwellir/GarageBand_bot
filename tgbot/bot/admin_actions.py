from datetime import timedelta

from django.utils.timezone import now
from telegram.error import BadRequest

from garage_band_bot.settings import ADMIN_GROUP_ID, PUBLISHING_CHANNEL_ID
from tgbot.bot.senders import send_message_return_id
from tgbot.exceptions import MessageDoesNotExistError, NoUserWithThisIdError
from tgbot.models import BotUser, RegisteredRequest


# todo organize exception control
def ban_user_by_id(bot, pk, callback=None):
    try:
        user = BotUser.objects.get(pk=pk)
    except BotUser.DoesNotExist:
        raise NoUserWithThisIdError(pk)
    user.ban()
    user_requests = RegisteredRequest.objects.filter(
        request__user=user, request__formed_at__gte=now() - timedelta(hours=24)
    )
    for request in user_requests.all():
        try:
            delete_channel_message_by_id(bot, request.message_id)
        except MessageDoesNotExistError:
            pass
    msg = {
        "text": f"Пользователь {user} забанен, его посты за последние сутки удалены!"
    }
    callback.answer(msg["text"])
    send_message_return_id(msg, ADMIN_GROUP_ID, bot)


def delete_channel_message_by_id(bot, message_id, callback=None):
    try:
        bot.delete_message(PUBLISHING_CHANNEL_ID, message_id)
    except BadRequest:
        raise MessageDoesNotExistError(message_id)
    if callback:
        msg = {"text": f"Сообщение #{message_id} удалено!"}
        callback.answer(msg["text"])
        send_message_return_id(msg, ADMIN_GROUP_ID, bot)


ADMIN_ACTIONS = {
    "admin_ban": ban_user_by_id,
    "admin_delete": delete_channel_message_by_id,
}
