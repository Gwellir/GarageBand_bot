import tempfile

from django.core.files import File
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from garage_band_bot.settings import ADMIN_GROUP_ID
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import DEFAULT_LOGO_FILE
from tgbot.bot.senders import publish_summary_return_id, send_message_return_id
from tgbot.bot_replies import get_admin_message, get_summary_for_request
from tgbot.exceptions import UserIsBannedError


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
        verbose_name="Полное имя пользователя", max_length=50, blank=True
    )
    first_name = models.CharField(verbose_name="Имя в ТГ", max_length=100, blank=True)
    last_name = models.CharField(
        verbose_name="Фамилия в ТГ", max_length=100, blank=True
    )
    user_id = models.PositiveIntegerField(
        verbose_name="ID в ТГ", unique=True, null=False, db_index=True
    )
    username = models.CharField(verbose_name="Ник в ТГ", null=True, max_length=50)
    location = models.CharField(
        verbose_name="Указанное местоположение", null=True, blank=True, max_length=100
    )
    phone = models.CharField(verbose_name="Номер телефона", blank=True, max_length=20)
    # todo move to some base TrackableModelMixin?
    last_active = models.DateTimeField(
        verbose_name="Время последней активности",
        auto_now=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Время создания",
        auto_now_add=True,
    )
    is_banned = models.BooleanField(
        verbose_name="В бане", default=False, null=False, db_index=True
    )
    is_staff = models.BooleanField(
        verbose_name="Админ", default=False, null=False, db_index=True
    )

    @property
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return (
            f"#{self.pk} {self.name if self.name else self.get_fullname} "
            f"TG: #{self.user_id} @{self.username if self.username else '-'}"
        )

    @classmethod
    def get_or_create(cls, data):
        user, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data
        )
        if user.is_banned:
            raise UserIsBannedError(user)

        return user, created

    def ban(self):
        if self.is_banned:
            raise UserIsBannedError(self)
        self.is_banned = True
        self.save()


class WorkRequest(models.Model):
    """Класс с заявками"""

    title = models.CharField(
        verbose_name="Наименование задачи", max_length=70, blank=True
    )
    description = models.TextField(
        verbose_name="Подробное описание", max_length=700, blank=True
    )
    formed_at = models.DateTimeField(
        verbose_name="Время составления", auto_now=True, db_index=True
    )
    user: BotUser = models.ForeignKey(BotUser, on_delete=models.CASCADE, db_index=True)
    location = models.CharField(
        verbose_name="Местоположение для ремонта", blank=True, max_length=100
    )
    is_complete = models.BooleanField(
        verbose_name="Флаг готовности заявки", default=False, db_index=True
    )
    dialog = models.OneToOneField(
        "Dialog",
        on_delete=models.SET_NULL,
        null=True,
        related_name="request",
        default=None,
    )
    # photos backref
    # registered backref

    @classmethod
    def get_or_create(cls, user, dialog):
        return WorkRequest.objects.get_or_create(
            user=user, dialog=dialog, is_complete=False
        )

    def data_as_dict(self):
        if self.is_complete:
            registered_pk = self.registered.pk
            registered_msg_id = self.registered.message_id
        else:
            registered_pk = registered_msg_id = "000"
        return dict(
            request_tag=self.title,
            request_desc=self.description,
            request_location=self.location,
            user_pk=self.user.pk,
            user_name=self.user.name,
            user_tg_id=self.user.user_id,
            registered_pk=registered_pk,
            registered_msg_id=registered_msg_id,
        )

    def get_photo(self):
        if self.photos.all():
            return self.photos.all()[0].tg_file_id
        else:
            return File(open(DEFAULT_LOGO_FILE, "rb"))

    @transaction.atomic
    def set_ready(self, bot):
        for photo in self.photos.all():
            file = bot.get_file(file_id=photo.tg_file_id)
            temp = tempfile.TemporaryFile()
            file.download(out=temp)
            photo.image.save(f"{photo.tg_file_id}.jpg", temp)
            temp.close()
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_READY.format(
                user_id=self.user.username,
                request_id=self.pk,
                photos_count=self.photos.count(),
            )
        )
        self.is_complete = True
        self.save()
        RegisteredRequest.publish(self, bot)


class RegisteredRequest(models.Model):
    request = models.OneToOneField(
        WorkRequest, on_delete=models.CASCADE, related_name="registered"
    )
    message_id = models.PositiveIntegerField(
        verbose_name="Идентификатор сообщения в канале", null=True, db_index=True
    )

    @classmethod
    @transaction.atomic
    def publish(cls, request, bot):
        reg_request = cls.objects.create(
            request=request,
        )
        message_id = publish_summary_return_id(
            get_summary_for_request(
                request.data_as_dict(), request.get_photo(), ready=True
            ),
            request.user,
            bot,
        )
        reg_request.message_id = message_id
        reg_request.save()
        send_message_return_id(
            get_admin_message(request.data_as_dict()), ADMIN_GROUP_ID, bot
        )


class RequestPhoto(models.Model):
    """Модель для хранения сопровождающих фотографий"""

    description = models.CharField(
        verbose_name="Описание фото", max_length=255, null=True
    )
    tg_file_id = models.CharField(
        verbose_name="ID файла в ТГ", max_length=255, blank=False
    )
    image = models.ImageField(verbose_name="Фотография", upload_to="user_photos")
    request = models.ForeignKey(
        WorkRequest, on_delete=models.CASCADE, related_name="photos", db_index=True
    )


class Dialog(models.Model):
    user = models.OneToOneField(
        BotUser, on_delete=models.CASCADE, related_name="dialog"
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
        dialog, d_created = cls.objects.update_or_create(
            user=user,
        )
        request, r_created = WorkRequest.get_or_create(user, dialog)

        # todo implement reloading request drafts

        return dialog
