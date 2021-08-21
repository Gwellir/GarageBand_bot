from django.apps import apps
from django.db import models, transaction

from tgbot.exceptions import ActionAlreadyCompletedError
from tgbot.models import BotUser, MessengerBot, TrackableUpdateCreateModel


class Dialog(TrackableUpdateCreateModel):
    """
    Модель диалога с пользователем

    Содержит связь с пользователем, этап диалога, флаг завершения
    и данные о времени начала и последнем сообщении пользователя.
    """

    bot: MessengerBot = models.ForeignKey(
        MessengerBot, on_delete=models.CASCADE, related_name="dialog", default=1
    )
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name="dialog")
    is_finished = models.BooleanField(
        verbose_name="Диалог завершён", default=False, db_index=True
    )

    def __str__(self):
        return f"{self.pk} {self.user} @{self.bound.stage_id}"

    @property
    def bound(self):
        return getattr(self, f"bound_{self.bot.get_bound_name()}")

    @classmethod
    @transaction.atomic()
    def get_or_create(cls, bot, user, load=None):
        """
        Получает из базы, либо создаёт структуру из пользователя, диалога и заявки.
        Если все связанные с пользователем диалоги завершены - формирует новую пару
        диалог-заявка.
        """

        if not load:
            dialog, d_created = cls.objects.get_or_create(
                bot=bot, user=user, is_finished=False
            )
            # request, r_created = WorkRequest.get_or_create(user, dialog)
            # todo make a factory
            Model = apps.get_model(app_label=bot.bound_app, model_name=bot.bound_object)
            bound, b_created = Model.get_or_create(user, dialog)
        else:
            load_filter = {f"bound_{bot.get_bound_name()}__registered__pk": load}
            dialog = Dialog.objects.get(bot=bot, user=user, **load_filter)
            if dialog.bound.is_locked:
                raise ActionAlreadyCompletedError(bot.get_bound_name(), load)
            curr_dialog = Dialog.objects.filter(
                bot=bot, user=user, is_finished=False
            ).first()
            if curr_dialog:
                curr_dialog.finish()

            dialog.bound.stage_id = dialog.bound.get_ready_stage()
            dialog.is_finished = False

        return dialog

    def finish(self):
        """
        Завершает диалог.

        Если связанная заявка не опубликована, ей выставляется флаг is_discarded,
        в ином случае - is_finished.
        """

        if not self.bound.is_complete:
            self.bound.is_discarded = True
            self.bound.save()
        self.is_finished = True
        self.save()


class Message(TrackableUpdateCreateModel):
    """
    Модель для хранения сообщений из диалога

    Содержи связь с диалогом, содержимое сообщения, стадию диалога на момент
    формирования, информацию о направлении и времени создания.
    """

    dialog = models.ForeignKey(
        Dialog, on_delete=models.CASCADE, related_name="messages", db_index=True
    )
    text = models.TextField(verbose_name="Текст сообщения")
    stage = models.PositiveSmallIntegerField(verbose_name="Стадия диалога")
    message_id = models.IntegerField(
        verbose_name="Номер сообщения", default=None, null=True
    )
    is_incoming = models.BooleanField(
        verbose_name="Входящее", db_index=True, default=True
    )
