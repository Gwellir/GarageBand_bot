"""Содержит логику ведения диалога с пользователем."""

from convoapp.models import Dialog, Message
from convoapp.replies import get_reply_for_stage, get_summary_for_request
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.utils import get_user_message_as_text
from tgbot.exceptions import BotProcessingError, IgnoreActionError
from tgbot.models import BotUser, RequestFormingStage


def get_request_state(message_data):
    """
    Возвращает номер заявки для подгрузки в процессор диалогов,
    если это требуется.
    """

    cb = message_data.get("callback")
    if cb and cb.startswith("leave_feedback "):
        try:
            request_num = int(cb.split()[1])
            return request_num, RequestFormingStage.DONE
        except ValueError:
            pass


class DialogProcessor:
    """Класс, отвечающий за ведение диалога с пользователем.

    Инициализируется инстансом диалога и данными пришедшего сообщения, передаёт
    входные данные на сохранение в процессоры полей таблиц БД, возвращает
    список сообщений, соответствующий стадии диалога и сообщению
    пользователя."""

    def __init__(self, user_data, message_data):
        self.user, _ = BotUser.get_or_create(user_data)
        self.dialog = Dialog.get_or_create(
            message_data["bot"], self.user, load=get_request_state(message_data)
        )
        self.bound = self.dialog.bound
        self.message_data = message_data

    # todo довольно сложно понимать, так как часть событий за процессинг происходит
    #  в одной стадии, а часть - в другой
    def process(self):
        """
        Входная точка обработчика диалогов.

        Сохраняет входящее и исходящие сообщения в логах, выполняет оперирование
        пришедшими данными, обрабатывает исключения процессинга данных в боте.
        Возвращает список сообщений для отправки пользователю.
        """

        current_log_stage = self.dialog.bound.stage_id
        Message.objects.create(
            dialog=self.dialog,
            stage=current_log_stage,
            message_id=self.message_data.get("id"),
            text=get_user_message_as_text(self.message_data),
        )
        messages = []
        BOT_LOG.debug(
            LogStrings.DIALOG_INCOMING_MESSAGE.format(
                user_id=self.user.username,
                stage=self.dialog.bound.stage,
                input_data=self.message_data,
            )
        )

        try:
            self._operate_data()
        except BotProcessingError as e:
            BOT_LOG.debug(
                LogStrings.DIALOG_INPUT_ERROR.format(
                    user_id=self.user.username,
                    stage=self.dialog.bound.stage,
                    args=e.args,
                )
            )
            messages.append({"text": f"{e.args[0]}"})
        except IgnoreActionError as e:
            BOT_LOG.debug(
                LogStrings.DIALOG_INPUT_ERROR.format(
                    user_id=self.user.username,
                    stage=self.dialog.bound.stage,
                    args=e.args,
                )
            )
            return []

        try:
            messages.append(
                get_reply_for_stage(self.bound.data_as_dict(), self.bound.stage_id)
            )
        # это может произойти, если часть пользователей находится в стадии,
        # которая больше не существует (todo сдвинуть стадии в БД?)
        except IndexError:
            self._restart()
            messages.append(
                get_reply_for_stage(
                    self.bound.data_as_dict(), RequestFormingStage.WELCOME
                )
            )

        if self.bound.stage_id == RequestFormingStage.CHECK_DATA:
            messages.append(
                get_summary_for_request(
                    self.bound.data_as_dict(), self.bound.get_photo()
                )
            )

        elif self.bound.stage_id in [
            RequestFormingStage.DONE,
            RequestFormingStage.FEEDBACK_DONE,
        ]:
            self.dialog.finish()

        return messages

    def _restart(self):
        """Выполняет переинициализацию диалога.
        (завершает текущий диалог, чтобы при следующем ответе пользователя
        создался новый)"""

        BOT_LOG.debug(
            LogStrings.DIALOG_RESTART.format(
                user_id=self.user.username,
                stage=self.bound.stage,
            )
        )

        self.dialog.finish()
        # this is not saved, just to assure correct messages are displayed
        self.bound.stage_id = RequestFormingStage.WELCOME

    def _advance_stage(self):
        """Выполняет выбор новой стадии диалога на основе входных данных."""

        callback = self.message_data["callback"]
        new_stage = None
        # если меняем стадию на первую, то реинициализируемся
        if callback == "restart":
            self._restart()
            return
        elif callback is not None:
            new_stage = self.bound.stage.get_by_callback(callback.split()[0])
        # todo this is now somewhat obsolete
        BOT_LOG.debug(
            LogStrings.DIALOG_CHANGE_STAGE.format(
                user_id=self.user.username,
                stage=self.bound.stage,
                new_stage=new_stage,
                callback=callback,
            )
        )
        if new_stage:
            self.bound.stage_id = new_stage
        self.bound.save()
        self.dialog.save()

    def _operate_data(self):
        """Применяет соответствующий стадии процессор к входным данным."""

        processor = self.bound.stage.get_processor()
        if processor:
            processor()(self, self.message_data)
        self._advance_stage()
