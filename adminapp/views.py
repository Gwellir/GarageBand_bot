from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from tgbot.models import BotUser, Dialog, Message


def get_registered_pk(dialog):
    if hasattr(dialog, "request") and hasattr(dialog.request, "registered"):
        return dialog.request.registered.pk


def get_message_id(dialog):
    if hasattr(dialog, "request") and hasattr(dialog.request, "registered"):
        return dialog.request.registered.message_id


def get_is_complete(dialog):
    return hasattr(dialog, "request") and dialog.request.is_complete


def get_tag(dialog):
    if hasattr(dialog, "request"):
        return dialog.request.tag
    return None


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def logs_list_view(request, user_pk=None, dialog_pk=None):
    """Отображает список проведённых чатов и содержимое просматриваемого чата."""

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

    return render(request, "adminapp/chat_view.html", context)
