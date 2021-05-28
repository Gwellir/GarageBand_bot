from django.core.files import File

import tgbot.bot.strings as strings
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import DEFAULT_LOGO_FILE, MAX_CAPTION_LENGTH
from tgbot.models import DialogStage

from ..exceptions import BotProcessingError
from .processors import (
    DescriptionInputProcessor,
    LocationInputProcessor,
    NameInputProcessor,
    PhoneNumberInputProcessor,
    SetReadyInputProcessor,
    StorePhotoInputProcessor,
    TitleInputProcessor,
)
from .senders import publish_summary

PROCESSORS = {
    DialogStage.STAGE3_GET_NAME: NameInputProcessor,
    DialogStage.STAGE4_GET_REQUEST_TITLE: TitleInputProcessor,
    DialogStage.STAGE5_GET_REQUEST_DESC: DescriptionInputProcessor,
    DialogStage.STAGE7_GET_PHOTOS: StorePhotoInputProcessor,
    DialogStage.STAGE8_GET_LOCATION: LocationInputProcessor,
    DialogStage.STAGE9_GET_PHONE: PhoneNumberInputProcessor,
    DialogStage.STAGE10_CHECK_DATA: SetReadyInputProcessor,
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

    return strings.stages_info[num]


class DialogProcessor:
    def __init__(self, dialog, message_data):
        self.dialog = dialog
        self.user = self.dialog.user
        self.request = self.dialog.request
        self.message_data = message_data

    def process(self):
        messages = []
        BOT_LOG.debug(
            LogStrings.DIALOG_INCOMING_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                input_data=self.message_data,
            )
        )
        try:
            self.operate_data()
            self.change_stage()
        except BotProcessingError as e:
            BOT_LOG.debug(
                LogStrings.DIALOG_INPUT_ERROR.format(
                    user_id=self.user.username,
                    stage=self.dialog.stage,
                    args=e.args,
                )
            )
            messages.append({"text": f"{e.args[0]}!"})
        messages.append(get_reply_for_stage(self.dialog.stage))
        if self.dialog.stage == DialogStage.STAGE10_CHECK_DATA:
            messages.append(self.get_summary_for_request())
        if self.dialog.stage == DialogStage.STAGE11_DONE:
            # move to request saving process
            publish_summary(
                self.get_summary_for_request(), self.user, self.message_data["bot"]
            )
            self.restart()

        return messages

    def restart(self):
        BOT_LOG.debug(
            LogStrings.DIALOG_RESTART.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
            )
        )
        self.dialog.delete()

    def change_stage(self):
        callback = self.message_data["callback"]
        if callback is not None:
            new_stage = CALLBACK_TO_STAGE[callback.data]
            callback.answer()
        else:
            new_stage = NEXT_STAGE.get(self.dialog.stage, self.dialog.stage)
        BOT_LOG.debug(
            LogStrings.DIALOG_CHANGE_STAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                new_stage=new_stage,
                callback=callback.data if callback else None,
            )
        )
        self.dialog.stage = new_stage
        self.dialog.save()

    def operate_data(self):
        callback = self.message_data["callback"]
        # todo по всему коду контроль критических состояний разбросан...
        # если меняем стадию на первую, то реинициализируемся
        if callback and callback.data == "restart":
            self.restart()
        elif self.dialog.stage in PROCESSORS.keys():
            PROCESSORS[self.dialog.stage]()(self, self.message_data)

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
        buttons = strings.summary["buttons"]
        if self.request.photos.all():
            photo = self.request.photos.all()[0].tg_file_id
        else:
            photo = File(open(DEFAULT_LOGO_FILE, "rb"))

        return dict(caption=text[:MAX_CAPTION_LENGTH], buttons=buttons, photo=photo)
