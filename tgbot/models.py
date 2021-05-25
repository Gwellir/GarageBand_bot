from io import BufferedReader, BufferedWriter, BytesIO

from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class DialogStage(models.IntegerChoices):
    STAGE1_WELCOME = 1, _("Стадия 1. Приветствие")
    STAGE2_CONFIRM_START = 2, _("Стадия 2. Подтвердить создание заявки")
    STAGE3_GET_NAME = 3, _("Стадия 3. Получить имя")
    STAGE4_GET_REQUEST_TITLE = 4, _("Стадия 4. Получить название заявки")
    STAGE5_GET_REQUEST_DESC = 5, _("Стадия 5. Получить описание заявки")
    STAGE6_REQUEST_PHOTOS = 6, _("Стадия 6. Предложить отправить фотографии")
    STAGE7_GET_PHOTOS = 7, _("Стадия 7. Получить фотографии")
    STAGE8_GET_LOCATION = 8, _("Стадия 8. Получить местоположение")
    STAGE9_GET_PHONE = 9, _("Стадия 9. Получить телефон")
    STAGE10_CHECK_DATA = 10, _("Стадия 10. Проверить заявку")
    STAGE11_DONE = 11, _("Стадия 11. Работа завершена")


class BotUser(models.Model):
    """Класс с информацией о пользователях бота"""

    name = models.CharField(
        verbose_name="Полное имя для бота", max_length=100, blank=True
    )
    first_name = models.CharField(
        verbose_name="Полное имя в ТГ", max_length=100, blank=True
    )
    last_name = models.CharField(
        verbose_name="Полное имя в ТГ", max_length=100, blank=True
    )
    user_id = models.PositiveIntegerField(
        verbose_name="ID в ТГ", unique=True, null=False
    )
    username = models.CharField(verbose_name="Ник в ТГ", null=True, max_length=100)
    location = models.CharField(
        verbose_name="Указанное местоположение", null=True, max_length=200
    )
    last_active = models.DateTimeField(
        verbose_name="Время последней активности", default=now
    )

    @property
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return (
            f"#{self.pk} {self.name if self.name else self.get_fullname} "
            f"TG: #{self.user_id} @{self.username}"
        )

    @classmethod
    def get_or_create(cls, data):
        user, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data
        )

        return user, created


class WorkRequest(models.Model):
    """Класс с заявками"""

    title = models.CharField(
        verbose_name="Наименование задачи", max_length=255, blank=True
    )
    description = models.TextField(verbose_name="Подробное описание", blank=True)
    formed_at = models.DateTimeField(verbose_name="Время составления", auto_now=True)
    user: BotUser = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    location = models.CharField(
        verbose_name="Местоположение для ремонта", blank=True, max_length=200
    )
    phone = models.CharField(verbose_name="Номер телефона", blank=True, max_length=50)
    is_complete = models.BooleanField(
        verbose_name="Флаг готовности заявки", default=False
    )
    # photos backref

    @classmethod
    def get_or_create(cls, user):
        # странное решение, может быть, завести модель уникальных черновиков заявок по пользователям?
        return WorkRequest.objects.get_or_create(user=user, is_complete=False)

    @transaction.atomic
    def set_ready(self, bot):
        for photo in self.photos.all():
            file = bot.get_file(file_id=photo.tg_file_id)
            wpo = BytesIO()
            w_write = BufferedWriter(wpo)
            w_read = BufferedReader(wpo)
            file.download(out=w_write)
            photo.image.save(f"{photo.tg_file_id}.jpg", w_read)
        self.is_complete = True
        self.save()


class RequestPhoto(models.Model):
    """Модель для хранения сопровождающих фотографий"""

    description = models.CharField(
        verbose_name="Описание фото", max_length=255, null=True
    )
    tg_file_id = models.CharField(
        verbose_name="ID файла в ТГ", max_length=100, blank=False
    )
    image = models.ImageField(verbose_name="Фотография", upload_to="user_photos")
    request = models.ForeignKey(
        WorkRequest, on_delete=models.CASCADE, related_name="photos"
    )


class Dialog(models.Model):
    user = models.OneToOneField(
        BotUser, on_delete=models.CASCADE, related_name="dialog"
    )
    request = models.OneToOneField(
        WorkRequest,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dialog",
        default=None,
    )
    stage = models.PositiveSmallIntegerField(
        verbose_name="Состояние диалога",
        choices=DialogStage.choices,
        null=False,
        default=DialogStage.STAGE1_WELCOME,
    )

    @classmethod
    @transaction.atomic()
    def get_or_create(cls, update):
        user, u_created = BotUser.get_or_create(update)
        request, r_created = WorkRequest.get_or_create(user)
        dialog, d_created = cls.objects.update_or_create(
            user=user,
            request=request,
        )
        # todo implement reloading request drafts

        return dialog
