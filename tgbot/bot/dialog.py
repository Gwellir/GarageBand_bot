from django.core.files import File
from django.db import IntegrityError
from telegram import ParseMode

import tgbot.bot.strings as strings
from tgbot.bot.constants import (
    DEFAULT_LOGO_FILE,
    MAX_CAPTION_LENGTH,
    PUBLISHING_CHANNEL_ID,
)
from tgbot.models import Dialog, DialogStage

from ..exceptions import BotProcessingError
from .processors import (
    DescriptionProcessor,
    LocationProcessor,
    NameProcessor,
    PhoneNumberProcessor,
    SetReadyProcessor,
    StorePhotoProcessor,
    TitleProcessor,
)
from .utils import build_button_markup, extract_user_data_from_update

PROCESSORS = {
    DialogStage.STAGE3_GET_NAME: NameProcessor,
    DialogStage.STAGE4_GET_REQUEST_TITLE: TitleProcessor,
    DialogStage.STAGE5_GET_REQUEST_DESC: DescriptionProcessor,
    DialogStage.STAGE7_GET_PHOTOS: StorePhotoProcessor,
    DialogStage.STAGE8_GET_LOCATION: LocationProcessor,
    DialogStage.STAGE9_GET_PHONE: PhoneNumberProcessor,
    DialogStage.STAGE10_CHECK_DATA: SetReadyProcessor,
}


CALLBACK_TO_STAGE = {
    "new_request": DialogStage.STAGE2_CONFIRM_START,
    "restart": DialogStage.STAGE1_WELCOME,
    # placeholders
    "search_request": DialogStage.STAGE1_WELCOME,
    "propose_ads": DialogStage.STAGE1_WELCOME,
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


def get_reply_for_stage(stage):
    num = stage - 1
    text = strings.stages_info[num]["text"]
    markup = build_button_markup(strings.stages_info[num]["buttons"])

    return dict(text=text, reply_markup=markup)


class DialogProcessor:
    def __init__(self, update):
        user_data = extract_user_data_from_update(update)
        self.dialog = Dialog.get_or_create(user_data)
        self.user = self.dialog.user
        self.request = self.dialog.request

    def process(self, update, context):
        msg = update.effective_message
        bot = context.bot
        input_data = {
            "bot": bot,
            "text": msg.text,
            "caption": msg.caption,
            "photo": msg.photo,
            "callback": update.callback_query,
        }
        try:
            self.operate_data(input_data)
            self.change_stage(input_data)
        except (IntegrityError, BotProcessingError) as e:
            print(e.args)
            self.send_got_wrong_data(bot)
        except AttributeError as e:
            # происходит, когда request не существует, например,
            # когда нажата кнопка из прошлых стадий диалога
            print(e.args)
            self.dialog.stage = DialogStage.STAGE1_WELCOME
            self.dialog.save()
        self.send_reply(get_reply_for_stage(self.dialog.stage), bot)
        if self.dialog.stage == DialogStage.STAGE10_CHECK_DATA:
            self.show_summary(self.get_summary_for_request(), bot)
        if self.dialog.stage == DialogStage.STAGE11_DONE:
            self.publish_summary(self.get_summary_for_request(), bot)
            self.restart()

    def restart(self):
        self.dialog.delete()
        # чтобы заявка, прикреплённая к диалогу, сбросилась
        self.request = None

    def change_stage(self, input_data):
        callback = input_data["callback"]
        if callback is not None:
            self.dialog.stage = CALLBACK_TO_STAGE[callback.data]
        else:
            self.dialog.stage = NEXT_STAGE.get(self.dialog.stage, self.dialog.stage)
        self.dialog.save()

    def operate_data(self, input_data):
        callback = input_data["callback"]
        # todo по всему коду контроль критических состояний разбросан...
        # если меняем стадию на первую, то реинициализируемся
        if callback and callback.data == "restart":
            self.restart()
        elif self.dialog.stage in PROCESSORS.keys():
            PROCESSORS[self.dialog.stage]()(self, input_data)

    def get_summary_for_request(self):
        text = strings.summary["text"] % (
            self.request.pk,
            self.request.title,
            f"{self.request.description[:700]}{' <...>' if len(self.request.description) > 700 else ''}",
            self.request.location,
            self.user.username,
            self.user.name,
            self.request.phone,
        )
        markup = build_button_markup(strings.summary["buttons"])
        if self.request.photos.all():
            photo = self.request.photos.all()[0].tg_file_id
        else:
            photo = File(open(DEFAULT_LOGO_FILE, "rb"))

        return dict(caption=text[:MAX_CAPTION_LENGTH], reply_markup=markup, photo=photo)

    def send_got_wrong_data(self, bot):
        bot.send_message(
            chat_id=self.user.user_id,
            text="Отправлены неверные данные, попробуйте ещё раз!",
        )

    def send_reply(self, reply, bot):
        bot.send_message(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN_V2, **reply
        )

    def show_summary(self, summary, bot):
        bot.send_photo(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN, **summary
        )

    def publish_summary(self, summary, bot):
        del summary["reply_markup"]
        bot.send_photo(
            chat_id=PUBLISHING_CHANNEL_ID, parse_mode=ParseMode.MARKDOWN, **summary
        )
