"""Содержит логику ведения диалога с пользователем."""

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings

from ..exceptions import BotProcessingError
from ..models import DialogStage, Message
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
from .replies import get_reply_for_stage, get_summary_for_request
from .utils import get_bot_message_as_text, get_user_message_as_text

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
    """Класс, отвечающий за ведение диалога с пользователем.

    Инициализируется инстансом диалога и данными пришедшего сообщения, передаёт
    входные данные на сохранение в процессоры полей таблиц БД, возвращает
    список сообщений, соответствующий стадии диалога и сообщению
    пользователя."""

    def __init__(self, dialog, message_data):
        self.dialog = dialog
        self.user = self.dialog.user
        self.request = self.dialog.request
        self.message_data = message_data

    # todo довольно сложно понимать, так как часть событий за процессинг происходит
    #  в одной стадии, а часть - в другой
    def process(self):
        """
        Входная точка обработчика диалогов.

        Сохраняет входящее и исходяшие сообщения в логах, выполняет оперирование
        пришедшими данными, обрабатывает исключения процессинга данных в боте.
        Возвращает список сообщений для отправки пользователю.
        """

        messages = []
        current_log_stage = self.dialog.stage
        BOT_LOG.debug(
            LogStrings.DIALOG_INCOMING_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
                input_data=self.message_data,
            )
        )
        Message.objects.create(
            dialog=self.dialog,
            stage=current_log_stage,
            text=get_user_message_as_text(self.message_data),
        )

        try:
            self._operate_data()
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
            self._restart()

        for message in messages:
            Message.objects.create(
                dialog=self.dialog,
                stage=current_log_stage,
                text=get_bot_message_as_text(message),
                is_incoming=False,
            )

        return messages

    def _restart(self):
        """Выполняет переинициализацию диалога.
        (завершает текущий диалог, чтобы при следующем ответе пользователя
        создался новый)"""

        BOT_LOG.debug(
            LogStrings.DIALOG_RESTART.format(
                user_id=self.user.username,
                stage=self.dialog.stage,
            )
        )

        self.dialog.finish()
        # this is not saved, just to assure correct messages are displayed
        self.dialog.stage = DialogStage.WELCOME

    def _advance_stage(self, step):
        """Выполняет выбор новой стадии диалога на основе входных данных."""

        callback = self.message_data["callback"]
        # если меняем стадию на первую, то реинициализируемся
        if callback == "restart":
            self._restart()
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

    def _operate_data(self):
        """Применяет соответствующий стадии процессор к входным данным.

        Возвращает сдвиг номера стадии перед следующей операцией."""

        step = 1
        if self.dialog.stage in PROCESSORS.keys():
            step = PROCESSORS[self.dialog.stage]()(self, self.message_data)
        self._advance_stage(step)
