"""Содержит классы моделей бота для ORM Django."""

import tempfile

from django.core.files import File
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from garage_band_bot.settings import ADMIN_GROUP_ID, PUBLISHING_CHANNEL_NAME
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import DEFAULT_LOGO_FILE
from tgbot.bot.replies import get_admin_message, get_summary_for_request
from tgbot.bot.senders import publish_summary_return_id, send_message_return_id
from tgbot.exceptions import UserIsBannedError


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


# todo merge with Django Auth User
class BotUser(models.Model):
    """
    Модель с информацией о пользователях бота.

    Содержит информацию из Telegram, а также данные, которые указывает пользователь
    в процессе оформления заявки (имя и телефон)
    """

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
        """Возвращает полное имя пользователя, как оно указано в Телеграме."""

        return f"{self.first_name} {self.last_name}"

    def stats_as_tg_html(self):
        rrs = RegisteredRequest.objects.filter(request__user=self).order_by('pk')
        if rrs.count() == 0:
            return None
        rrs_str = ""
        for rr in rrs:
           rrs_str = f"{rrs_str} {rr.as_tg_html()}"
        return f'<a href="tg://user?id={self.user_id}">#{self.pk} {self.name}</a>:' \
               f'{rrs_str}'

    def __str__(self):
        return (
            f"#{self.pk} {self.name if self.name else self.get_fullname} "
            f"TG: #{self.user_id} @{self.username if self.username else '-'}"
        )

    @classmethod
    def get_or_create(cls, data):
        """
        Возвращает новый или существующий инстанс пользователя.

        Вызывает UserIsBannerError, если пользователь забанен.
        """

        user, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data
        )
        if user.is_banned:
            raise UserIsBannedError(user)

        return user, created

    def ban(self):
        """
        Устанавливает пользователю флаг бана.

        Вызывает UserIsBannerError, если пользователь УЖЕ забанен.
        """

        if self.is_banned:
            raise UserIsBannedError(self)
        self.is_banned = True
        self.save()


class Tag(models.Model):
    """Модель со списком разновидностей категорий заявок."""

    name = models.CharField(verbose_name="Наименование", max_length=255, blank=False)

    def __str__(self):
        return f"#{self.pk} {self.name}"


class WorkRequest(models.Model):
    """
    Модель заявки

    Содержит все введённые пользователем данные, относящиеся к ремонту,
    связь с пользователем и диалогом, флаги состояния и время создания.
    """

    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, db_index=True, null=True)
    title = models.CharField(
        verbose_name="Наименование задачи", max_length=70, blank=True
    )
    description = models.TextField(
        verbose_name="Подробное описание", max_length=700, blank=True
    )
    formed_at = models.DateTimeField(
        verbose_name="Время составления", auto_now=True, db_index=True
    )
    user: BotUser = models.ForeignKey(BotUser, on_delete=models.CASCADE, db_index=True, related_name='requests')
    location = models.CharField(
        verbose_name="Местоположение для ремонта", blank=True, max_length=100
    )
    car_type = models.CharField(
        verbose_name="Тип автомобиля", blank=True, max_length=50
    )
    is_complete = models.BooleanField(
        verbose_name="Флаг готовности заявки", default=False, db_index=True
    )
    is_discarded = models.BooleanField(
        verbose_name="Флаг отказа от проведения заявки", default=False, db_index=True
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

    def __str__(self):
        return f"#{self.pk} {self.user} {self.tag} {self.is_complete}"

    @classmethod
    def get_or_create(cls, user, dialog):
        """
        Возвращает заявку, которая привязана к пользователю и диалогу,
        или же формирует новую.
        Заявка считается завершённой, либо если она зарегистрирована,
        либо если отброшена.
        """

        return WorkRequest.objects.get_or_create(
            user=user, dialog=dialog, is_complete=False, is_discarded=False
        )

    # todo separate into a manager?
    def data_as_dict(self):
        """
        Возвращает данные, релевантные для формирования ответов пользователям,
        в виде словаря.
        """

        if self.is_complete:
            registered_pk = self.registered.pk
            registered_msg_id = self.registered.message_id
        else:
            registered_pk = registered_msg_id = "000"
        if self.tag:
            tag_name = self.tag.name.replace("/", "_").replace(" ", "_")
        else:
            tag_name = None
        return dict(
            channel_name=PUBLISHING_CHANNEL_NAME,
            request_tag=tag_name,
            request_desc=self.description,
            request_car_type=self.car_type,
            user_pk=self.user.pk,
            user_name=self.user.name,
            user_tg_id=self.user.user_id,
            registered_pk=registered_pk,
            registered_msg_id=registered_msg_id,
        )

    def get_photo(self):
        """
        Возвращает объект фотографии, пригодный для передачи в Телеграм.

        Либо первое из загруженных фото, либо картинку по умолчанию, если
        фотографии не были загружены.
        """

        if self.photos.all():
            return self.photos.all()[0].tg_file_id
        else:
            return File(open(DEFAULT_LOGO_FILE, "rb"))

    @transaction.atomic
    def set_ready(self, bot):
        """
        Выставляет заявке статус готовности.

        Загружает фотографии в базу данных, ставит отметку в логе, выставляет флаг
        готовности, а затем публикует заявку в канал
        """

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
    """
    Модель зарегистрированных заявок

    Содержит связь с заявкой, а также информацию о посте в канале (номер сообщения)
    """

    request = models.OneToOneField(
        WorkRequest, on_delete=models.CASCADE, related_name="registered"
    )
    message_id = models.PositiveIntegerField(
        verbose_name="Идентификатор сообщения в канале", null=True, db_index=True
    )

    def __str__(self):
        return f"{self.pk} {self.request.user} ({self.message_id})"

    def as_tg_html(self):
        return f'<a href="https://t.me/{PUBLISHING_CHANNEL_NAME}/{self.message_id}">#{self.pk}</a>'

    @classmethod
    @transaction.atomic
    def publish(cls, request, bot):
        """Публикует сообщение на базе заявки в основной канал,
        сохраняет номер сообщения."""

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
        request.save()
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
    """
    Модель диалога с пользователем

    Содержит связь с пользователем, этап диалога, флаг завершения
    и данные о времени начала и последнем сообщении пользователя.
    """

    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name="dialog")
    stage = models.PositiveSmallIntegerField(
        verbose_name="Состояние диалога",
        choices=DialogStage.choices,
        null=False,
        default=DialogStage.WELCOME,
    )
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
        return f"{self.pk} {self.user} @{self.stage}"

    @classmethod
    @transaction.atomic()
    def get_or_create(cls, update):
        """
        Получает из базы, либо создаёт структуру из пользователя, диалога и заявки.
        Если все связанные с пользователем диалоги завершены - формирует новую пару
        диалог-заявка.
        """

        user, u_created = BotUser.get_or_create(update)
        dialog, d_created = cls.objects.get_or_create(user=user, is_finished=False)
        request, r_created = WorkRequest.get_or_create(user, dialog)

        # todo implement reloading request drafts

        return dialog

    def finish(self):
        """
        Завершает диалог.

        Если связанная заявка не опубликована, ей выставляется флаг is_discarded,
        в ином случае - is_finished.
        """

        if not self.request.is_complete:
            self.request.is_discarded = True
            self.request.save()
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
    is_incoming = models.BooleanField(
        verbose_name="Входящее", db_index=True, default=True
    )
    created_at = models.DateTimeField(
        verbose_name="Время создания", auto_now_add=True, db_index=True
    )
