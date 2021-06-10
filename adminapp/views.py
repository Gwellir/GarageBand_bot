from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from tgbot.models import BotUser, Dialog, Message


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def logs_list_view(request, user_pk=None, dialog_pk=None):
    """Отображает список проведённых чатов и содержимое просматриваемого чата."""

    users = [
        {
            "number": user.pk,
            "name": user.username,
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
                "tag": dialog.request.tag if hasattr(dialog, "request") else None,
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
