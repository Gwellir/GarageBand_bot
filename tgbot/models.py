from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .bot.utils import extract_user_data_from_update


class DialogStage(models.IntegerChoices):
    STAGE1_WELCOME = 1, _("Стадия 1. Приветствие")
    STAGE2_CONFIRM_START = 2, _("Стадия 2. Подтвердить создание заявки")
    STAGE3_GET_NAME = 3, _("Стадия 3. Получить имя")
    STAGE4_GET_REQUEST_NAME = 4, _("Стадия 4. Получить название заявки")


class BotUser(models.Model):
    """Класс с информацией о пользователях бота"""

    name = models.CharField(verbose_name="Полное имя для бота", max_length=100, blank=True)
    first_name = models.CharField(verbose_name="Полное имя в ТГ", max_length=100, blank=True)
    last_name = models.CharField(verbose_name="Полное имя в ТГ", max_length=100, blank=True)
    user_id = models.PositiveIntegerField(verbose_name="ID в ТГ", unique=True, null=False)
    username = models.CharField(verbose_name="Ник в ТГ", null=True, max_length=100)
    location = models.CharField(verbose_name="Указанное местоположение", null=True, max_length=200)
    dialog_stage = models.PositiveSmallIntegerField(
        verbose_name="Состояние диалога",
        choices=DialogStage.choices,
        null=False,
        default=DialogStage.STAGE1_WELCOME
    )
    last_active = models.DateTimeField(verbose_name="Время последней активности", default=now)

    @property
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"#{self.pk} {self.name if self.name else self.get_fullname} " \
               f"TG: #{self.user_id} @{self.username}, stage: {self.dialog_stage}"

    @classmethod
    def get_or_create(cls, update, context):
        data = extract_user_data_from_update(update)
        user, created = cls.objects.update_or_create(
            user_id=data["user_id"],
            defaults=data
        )

        return user, created


class Request(models.Model):
    """Класс с заявками"""

    title = models.CharField(verbose_name="Наименование задачи", max_length=255, blank=False)
    description = models.TextField(verbose_name="Подробное описание", blank=True)
    formed_at = models.DateTimeField(verbose_name="Время составления", auto_now=True)
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    location = models.CharField(verbose_name="Местоположение для ремонта", blank=True, max_length=200)
    phone = models.CharField(verbose_name="Номер телефона", blank=True, max_length=50)
    # photos backref


class RequestPhoto(models.Model):
    """Модель для хранения сопровождающих фотографий"""

    description = models.CharField(verbose_name="Описание фото", max_length=255, blank=True)
    image = models.ImageField(verbose_name="Фотография", blank=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='photos')