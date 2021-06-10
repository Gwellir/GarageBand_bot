from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings

from ..bot_replies import get_reply_for_stage, get_summary_for_request
from ..exceptions import BotProcessingError
from ..models import DialogStage
from .processors import (
    DescriptionInputProcessor,
    LocationInputProcessor,
    NameInputProcessor,
    PhoneNumberInputProcessor,
    SetReadyInputProcessor,
    StartInputProcessor,
    StorePhotoInputProcessor,
    TagInputProcessor,
)

PROCESSORS = {
    DialogStage.WELCOME: StartInputProcessor,
    DialogStage.GET_NAME: NameInputProcessor,
    DialogStage.GET_REQUEST_TAG: TagInputProcessor,
    DialogStage.GET_REQUEST_DESC: DescriptionInputProcessor,
    DialogStage.REQUEST_PHOTOS: StorePhotoInputProcessor,
    DialogStage.GET_LOCATION: LocationInputProcessor,
    DialogStage.GET_PHONE: PhoneNumberInputProcessor,
    DialogStage.CHECK_DATA: SetReadyInputProcessor,
}


CALLBACK_TO_STAGE = {
    "new_request": DialogStage.GET_NAME,
    "restart": DialogStage.WELCOME,
    "final_confirm": DialogStage.DONE,
}


class DialogProcessor:
    def __init__(self, dialog, message_data):
        self.dialog = dialog
        self.user = self.dialog.user
        self.request = self.dialog.request
        self.message_data = message_data

    # todo довольно сложно понимать, так как часть событий за процессинг происходит
    #  в одной стадии, а часть - в другой
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
        except BotProcessingError as e:
            BOT_LOG.debug(
                LogStrings.DIALOG_INPUT_ERROR.format(
                    user_id=self.user.username,
                    stage=self.dialog.stage,
                    args=e.args,
                )
            )
            messages.append({"text": f"{e.args[0]}"})

        messages.append(
            get_reply_for_stage(self.request.data_as_dict(), self.dialog.stage)
        )

        if self.dialog.stage == DialogStage.CHECK_DATA:
            messages.append(
                get_summary_for_request(
                    self.request.data_as_dict(), self.request.get_photo()
                )
            )

        elif self.dialog.stage == DialogStage.DONE:
            self.restart()

        return messages

    def restart(self):
        BOT_LOG.debug(
            LogStrings.DIALOG_RESTART.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
            )
        )

        self.dialog.finish()

    def advance_stage(self, step):
        callback = self.message_data["callback"]
        # если меняем стадию на первую, то реинициализируемся
        if callback == "restart":
            self.restart()
            return
        elif callback is not None:
            new_stage = CALLBACK_TO_STAGE[callback]
        else:
            new_stage = self.dialog.stage + step
        BOT_LOG.debug(
            LogStrings.DIALOG_CHANGE_STAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                new_stage=new_stage,
                callback=callback,
            )
        )
        self.dialog.stage = new_stage
        self.dialog.save()

    def operate_data(self):
        step = 1
        if self.dialog.stage in PROCESSORS.keys():
            step = PROCESSORS[self.dialog.stage]()(self, self.message_data)
        self.advance_stage(step)
