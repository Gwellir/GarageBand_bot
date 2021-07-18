from django.apps import apps
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from tgbot.models import BotUser, MessengerBot


class DialogStage(models.IntegerChoices):
    """Набор стадий проведения диалога."""

    WELCOME = 1, _("Приветствие")
    GET_NAME = 2, _("Получить имя")
    GET_REQUEST_TAG = 3, _("Получить категорию заявки")
    GET_CAR_TYPE = 4, _("Получить тип автомобиля")
    GET_REQUEST_DESC = 5, _("Получить описание заявки")
    REQUEST_PHOTOS = 6, _("Предложить отправить фотографии")
    CHECK_DATA = 7, _("Проверить заявку")
    DONE = 8, _("Работа завершена")
    LEAVE_FEEDBACK = 9, _("Оставить отзыв")
    FEEDBACK_DONE = 10, _("Отзыв получен")


class Dialog(models.Model):
    """
    Модель диалога с пользователем

    Содержит связь с пользователем, этап диалога, флаг завершения
    и данные о времени начала и последнем сообщении пользователя.
    """

    bot = models.ForeignKey(
        MessengerBot, on_delete=models.CASCADE, related_name="dialog", default=1
    )
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name="dialog")
    is_finished = models.BooleanField(
        verbose_name="Диалог завершён", default=False, db_index=True
    )
    last_active = models.DateTimeField(
        verbose_name="Время последней активности",
        auto_now=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Время создания",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.pk} {self.user} @{self.bound.stage_id}"

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
            Model = apps.get_model(app_label="tgbot", model_name=bot.bound_object)
            bound, b_created = Model.get_or_create(user, dialog)
        else:
            curr_dialog = Dialog.objects.filter(
                bot=bot, user=user, is_finished=False
            ).first()
            if curr_dialog:
                curr_dialog.finish()
            dialog = Dialog.objects.get(
                bot=bot, user=user, bound__registered__pk=load[0]
            )
            dialog.stage = load[1]
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


class Message(models.Model):
    """
    Модель для хранения сообщений из диалога

    Содержи связь с диалогом, содержимое сообщения, стадию диалога на момент
    формирования, информацию о направлении и времени создания.
    """

    dialog = models.ForeignKey(
        Dialog, on_delete=models.CASCADE, related_name="messages", db_index=True
    )
    text = models.TextField(verbose_name="Текст сообщения")
    stage = models.PositiveSmallIntegerField(
        verbose_name="Стадия диалога", choices=DialogStage.choices
    )
    message_id = models.IntegerField(
        verbose_name="Номер сообщения", default=None, null=True
    )
    is_incoming = models.BooleanField(
        verbose_name="Входящее", db_index=True, default=True
    )
    created_at = models.DateTimeField(
        verbose_name="Время создания", auto_now_add=True, db_index=True
    )
