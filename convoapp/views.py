from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from convoapp.models import Dialog, Message
from tgbot.models import BotUser


def get_registered_pk(dialog):
    """
    Получает номер связанной с диалогом зарегистрированной заявки,
    если к диалогу привязана заявка и она зарегистрирована.

    :type dialog: :class:`convoapp.models.Dialog`
    """

    if hasattr(dialog, "bound") and hasattr(dialog.bound, "registered"):
        return dialog.bound.registered.pk
    return None


def get_message_id(dialog):
    """
    Получает номер опубликованного сообщения с заявкой, в случае, если
    к диалогу привязана заявка и она зарегистрирована.

    :type dialog: :class:`convoapp.models.Dialog`
    """

    if hasattr(dialog, "bound") and hasattr(dialog.bound, "registered"):
        return dialog.bound.registered.channel_message_id
    return None


def get_is_complete(dialog):
    """
    Получает статус завершённости заявки, в случае, если к диалогу привязана заявка.

    :type dialog: :class:`convoapp.models.Dialog`
    """

    return hasattr(dialog, "bound") and dialog.bound.is_complete


def get_is_discarded(dialog):
    """
    Получает статус отмены заявки, в случае, если к диалогу привязана заявка.

    :type dialog: :class:`convoapp.models.Dialog`
    """

    return hasattr(dialog, "bound") and dialog.bound.is_discarded


def get_tag(dialog):
    """
    Получает тег заявки, в случае, если к диалогу привязана заявка.

    :type dialog: :class:`convoapp.models.Dialog`
    """

    if hasattr(dialog, "bound"):
        return dialog.bound.tag
    return None


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def logs_list_view(request, user_pk=None, dialog_pk=None):
    """
    Отображает список пользователей, диалогов выбранного пользователя и
    содержимое выбранного диалога.

    :type request: :class:`django.http.HttpRequest`
    :type user_pk: int
    :type dialog_pk: int
    """

    users = [
        {
            "number": user.pk,
            "tg_id": user.user_id,
            "username": user.username,
            "fullname": user.get_fullname,
            "chat_last_message": None,
            "time": user.last_active,
            "is_banned": user.is_banned,
        }
        for user in BotUser.objects.all().order_by("-last_active").select_related()
    ]

    dialogs = []
    if user_pk:
        dialogs = [
            {
                "number": dialog.pk,
                "registered_pk": get_registered_pk(dialog),
                "message_id": get_message_id(dialog),
                "tag": get_tag(dialog),
                "is_complete": get_is_complete(dialog),
                "is_discarded": get_is_discarded(dialog),
                "time": dialog.last_active,
            }
            for dialog in Dialog.objects.filter(user__pk=user_pk).order_by(
                "-last_active", "-pk"
            )
        ]
    messages = []
    if dialog_pk:
        messages = [
            {
                "number": message.pk,
                "content": message.text,
                "direction": bool(message.is_incoming % 2),
                "time": message.created_at,
            }
            for message in Message.objects.filter(dialog__pk=dialog_pk).order_by(
                "created_at"
            )
        ]
    context = {
        "title_page": "Список чатов",
        "user_list": users,
        "chat_list": dialogs,
        "message_list": messages,
        "selected_user": user_pk,
        "selected_dialog": dialog_pk,
    }

    return render(request, "convoapp/chat_view.html", context)
