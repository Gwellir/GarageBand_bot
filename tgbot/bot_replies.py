from django.core.files import File

from tgbot.bot import strings as strings
from tgbot.bot.constants import DEFAULT_LOGO_FILE, MAX_CAPTION_LENGTH


def get_reply_for_stage(stage):
    num = stage - 1

    return strings.stages_info[num]


def get_admin_message(request):
    text = strings.admin["text"] % (
        request.registered.pk,
        request.user.user_id,
        request.user.name,
    )
    buttons = [
        [
            {
                "text": "❌ Удалить",
                "callback_data": f"admin_delete {request.registered.message_id}",
            }
        ],
        [
            {
                "text": "☠️ Забанить пользователя",
                "callback_data": f"admin_ban {request.user.pk}",
            }
        ],
    ]

    return dict(text=text, buttons=buttons)


def get_summary_for_request(request, ready=False):
    text = strings.summary["text"] % (
        request.registered.pk if ready else "000",
        request.title,
        f"{request.description[:700]}"
        f"{' <...>' if len(request.description) > 700 else ''}",
        request.location,
        request.user.user_id,
        request.user.name,
        request.phone,
    )
    buttons = strings.summary["buttons"]
    if request.photos.all():
        photo = request.photos.all()[0].tg_file_id
    else:
        photo = File(open(DEFAULT_LOGO_FILE, "rb"))

    return dict(caption=text[:MAX_CAPTION_LENGTH], buttons=buttons, photo=photo)
