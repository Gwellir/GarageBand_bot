import telegram
from django.core.files import File

from .constants import DEFAULT_LOGO_FILE
import tgbot.bot.strings as strings
from tgbot.models import DialogStage, RequestPhoto, WorkRequest


def build_button_markup(buttons_data):
    layout = []
    if buttons_data:
        for row in buttons_data:
            layout.append([telegram.InlineKeyboardButton(**item) for item in row])

        return telegram.InlineKeyboardMarkup(layout)

    return None


def get_reply_for_stage(stage):
    num = stage - 1
    text = strings.stages_info[num]["text"]
    markup = build_button_markup(strings.stages_info[num]["buttons"])

    return dict(text=text, reply_markup=markup)


def get_summary_for_request(request):
    text = strings.summary["text"] % (
        request.title,
        request.description,
        request.phone,
        request.user.username,
    )
    markup = build_button_markup(strings.summary["buttons"])
    if request.photos.all():
        photo = request.photos.all()[0].tg_file_id
    else:
        photo = File(open(DEFAULT_LOGO_FILE, 'rb'))

    return dict(caption=text, reply_markup=markup, photo=photo)


def set_name(context, update, user, request: WorkRequest):
    user.name = update.effective_message.text
    user.save()

    return user, request


def init_request_by_title(context, update, user, request: WorkRequest):
    title = update.effective_message.text
    request = WorkRequest.objects.create(
        user=user,
        title=title,
    )
    request.save()

    return user, request


def set_request_description(context, update, user, request: WorkRequest):
    desc = update.effective_message.text
    request.description = desc
    request.save()

    return user, request


def store_photo(context, update, user, request: WorkRequest):
    description = update.effective_message.caption
    if not description:
        description = ""
    if update.effective_message.photo:
        photo_file_id = update.effective_message.photo[-1].file_id
        photo = RequestPhoto(
            description=description,
            request=request,
            tg_file_id=photo_file_id,
        )
        photo.save()

    return user, request


def set_location(context, update, user, request):
    location = update.effective_message.text
    request.location = location
    request.save()

    return user, request


def set_phone(context, update, user, request):
    phone_number = update.effective_message.text
    request.phone = phone_number
    request.save()

    return user, request


def ready_request(context, update, user, request):
    request.set_ready(context.bot)

    return user, request


PROCESSORS = {
    DialogStage.STAGE3_GET_NAME: set_name,
    DialogStage.STAGE4_GET_REQUEST_TITLE: init_request_by_title,
    DialogStage.STAGE5_GET_REQUEST_DESC: set_request_description,
    DialogStage.STAGE7_GET_PHOTOS: store_photo,
    DialogStage.STAGE8_GET_LOCATION: set_location,
    DialogStage.STAGE9_GET_PHONE: set_phone,
    DialogStage.STAGE10_CHECK_DATA: ready_request,
}


CALLBACK_TO_STAGE = {
    "new_request": DialogStage.STAGE2_CONFIRM_START,
    "restart": DialogStage.STAGE1_WELCOME,
    "stage2_confirm": DialogStage.STAGE3_GET_NAME,
    "have_photos": DialogStage.STAGE7_GET_PHOTOS,
    "skip_photos": DialogStage.STAGE8_GET_LOCATION,
    "photos_confirm": DialogStage.STAGE8_GET_LOCATION,
    "final_confirm": DialogStage.STAGE11_DONE,
}

NEXT_STAGE = {
    DialogStage.STAGE1_WELCOME: DialogStage.STAGE1_WELCOME,
    DialogStage.STAGE3_GET_NAME: DialogStage.STAGE4_GET_REQUEST_TITLE,
    DialogStage.STAGE4_GET_REQUEST_TITLE: DialogStage.STAGE5_GET_REQUEST_DESC,
    DialogStage.STAGE5_GET_REQUEST_DESC: DialogStage.STAGE6_REQUEST_PHOTOS,
    DialogStage.STAGE7_GET_PHOTOS: DialogStage.STAGE7_GET_PHOTOS,
    DialogStage.STAGE8_GET_LOCATION: DialogStage.STAGE9_GET_PHONE,
    DialogStage.STAGE9_GET_PHONE: DialogStage.STAGE10_CHECK_DATA,
    DialogStage.STAGE11_DONE: DialogStage.STAGE1_WELCOME,
}
