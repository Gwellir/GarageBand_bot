"""Содержит логику ведения диалога с пользователем."""

from convoapp.models import Dialog, Message
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.utils import get_user_message_as_text
from tgbot.exceptions import BotProcessingError, IgnoreActionError
from tgbot.models import BotUser


def get_bound_state(message_data):
    """
    Возвращает номер заявки для подгрузки в процессор диалогов,
    если это требуется.
    """

    cb = message_data.get("callback")
    if not cb:
        return
    command = cb.split(" ")
    if command[0] in ["leave_feedback", "complete", "renew"]:
        try:
            bound_num = int(cb.split()[1])
            return bound_num
        except ValueError:
            pass


class DialogProcessor:
    """Класс, отвечающий за ведение диалога с пользователем.

    Инициализируется инстансом диалога и данными пришедшего сообщения, передаёт
    входные данные на сохранение в процессоры полей таблиц БД, возвращает
    список сообщений, соответствующий стадии диалога и сообщению
    пользователя."""

    users_cache = {}

    def __init__(self, user_data, message_data):
        self.user, self.dialog = self._load_models(user_data, message_data)
        self.bound = self.dialog.bound
        self.message_data = message_data
        self.suppress_output = False

    def _load_models(self, user_data, message_data):
        user_id = user_data.get("user_id")
        bot = message_data["bot"]
        cached_info = self.users_cache.get((bot, user_id))
        bound_state = get_bound_state(message_data)
        if not cached_info or bound_state:
            user, _ = BotUser.get_or_create(user_data)
            dialog = Dialog.get_or_create(message_data["bot"], user, load=bound_state)
            self.users_cache[(bot, user_id)] = user, dialog
        else:
            user, dialog = cached_info

        return user, dialog

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

        if not self.suppress_output:
            try:
                messages.append(self.bound.get_reply_for_stage())
            # это может произойти, если часть пользователей находится в стадии,
            # которая больше не существует (todo сдвинуть стадии в БД?)
            except IndexError:
                self._restart()
                messages.append(self.bound.get_reply_for_stage())

        if self.bound.check_data():
            messages.append(self.bound.get_summary())

        elif self.bound.is_done():
            self._restart()
            # self.dialog.finish()

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
        bot = self.message_data["bot"]
        self.users_cache.pop((bot, self.user.user_id))
        # this is not saved, just to assure correct messages are displayed
        self.bound.restart()

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
