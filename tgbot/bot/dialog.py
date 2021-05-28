from django.core.files import File
from telegram import ParseMode

import tgbot.bot.strings as strings
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
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
        BOT_LOG.debug(
            LogStrings.DIALOG_INCOMING_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                input_data=input_data,
            )
        )
        try:
            self.operate_data(input_data)
            self.change_stage(input_data)
        except BotProcessingError as e:
            BOT_LOG.debug(
                LogStrings.DIALOG_INPUT_ERROR.format(
                    user_id=self.user.username,
                    stage=self.dialog.stage,
                    args=e.args,
                )
            )
            self.send_reply({"text": f"{e.args[0]}\!"}, bot)
        self.send_reply(get_reply_for_stage(self.dialog.stage), bot)
        if self.dialog.stage == DialogStage.STAGE10_CHECK_DATA:
            self.show_summary(self.get_summary_for_request(), bot)
        if self.dialog.stage == DialogStage.STAGE11_DONE:
            self.publish_summary(self.get_summary_for_request(), bot)
            self.restart()

    def restart(self):
        BOT_LOG.debug(
            LogStrings.DIALOG_RESTART.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
            )
        )
        self.dialog.delete()

    def change_stage(self, input_data):
        callback = input_data["callback"]
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

    def send_reply(self, reply, bot):
        BOT_LOG.debug(
            LogStrings.DIALOG_SEND_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                reply=reply,
            )
        )
        bot.send_message(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN_V2, **reply
        )

    def show_summary(self, summary, bot):
        BOT_LOG.debug(
            LogStrings.DIALOG_SEND_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                reply=summary,
            )
        )
        bot.send_photo(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN, **summary
        )

    def publish_summary(self, summary, bot):
        del summary["reply_markup"]
        BOT_LOG.debug(
            LogStrings.DIALOG_PUBLISH_REQUEST.format(
                user_id=self.user.username,
                channel=PUBLISHING_CHANNEL_ID,
                summary=summary,
            )
        )
        bot.send_photo(
            chat_id=PUBLISHING_CHANNEL_ID, parse_mode=ParseMode.MARKDOWN, **summary
        )
