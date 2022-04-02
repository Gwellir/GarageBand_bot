"""Содержит классы моделей бота для ORM Django."""

import tempfile

from django.apps import apps
from django.core.files import File
from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from telegram.error import BadRequest, TimedOut

from abstract.models import (
    CacheableFillDataModel,
    LocationRegionBindModel,
    TrackableUpdateCreateModel,
)
from bazaarapp.processors import (
    LocationConfirmationProcessor,
    LocationKeyInputProcessor,
)
from convoapp.processors import (
    CarTypeInputProcessor,
    DescriptionInputProcessor,
    FeedbackInputProcessor,
    NameInputProcessor,
    SetReadyInputProcessor,
    StartInputProcessor,
    StorePhotoInputProcessor,
    TagInputProcessor,
)
from garage_band_bot.settings import DEBUG
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from repairsapp import strings as repair_strings
from tgbot.apps import tg_dispatchers, tg_updaters
from tgbot.bot.constants import DEFAULT_LOGO_FILE
from tgbot.bot.senders import send_messages_return_ids
from tgbot.exceptions import UserIsBannedError


class TGInstance(models.Model):
    """Модель, описывающая инстанс бота в телеграме"""

    token = models.CharField(
        verbose_name="Токен ТГ", max_length=50, blank=False, db_index=True
    )
    publish_id = models.BigIntegerField(verbose_name="Основной канал бота", blank=False)
    publish_name = models.CharField(
        verbose_name="Название канала", max_length=100, blank=False
    )
    admin_group_id = models.BigIntegerField(
        verbose_name="Группа администрирования", null=True
    )
    discussion_group_id = models.BigIntegerField(
        verbose_name="Группа обсуждения", null=True
    )
    feedback_group_id = models.BigIntegerField(verbose_name="Группа фидбека", null=True)
    # bot backref

    @property
    def tg_bot(self):
        try:
            return tg_updaters.get(self.token).bot
        except (NameError, KeyError, AttributeError):
            return tg_dispatchers.get(self.token)

    @property
    def job_queue(self):
        return tg_updaters.get(self.token).job_queue


class MessengerBot(models.Model):
    """Модель, описывающая бота, предназначенного для конкретной цели"""

    name = models.CharField(verbose_name="Наименование", max_length=150)
    bound_app = models.CharField(
        verbose_name="Приложение для обработки объекта",
        max_length=50,
        blank=False,
        default="tgbot",
    )
    bound_object = models.CharField(
        verbose_name="Рабочий объект", max_length=50, blank=False
    )
    telegram_instance = models.OneToOneField(
        TGInstance,
        related_name="bot",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    is_active = models.BooleanField(
        verbose_name="Бот включён", default=True, db_index=True
    )
    is_debug = models.BooleanField(
        verbose_name="Для дебага",
        default=True,
        db_index=True,
    )

    def get_bound_model(self):
        return apps.get_model(app_label=self.bound_app, model_name=self.bound_object)

    def get_bound_name(self):
        return self.bound_object.lower()

    @classmethod
    def get_by_model_name(cls, name):
        return cls.objects.get(bound_object=name, is_debug=DEBUG, is_active=True)


# todo merge with Django Auth User
class BotUser(TrackableUpdateCreateModel):
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
    user_id = models.PositiveBigIntegerField(
        verbose_name="ID в ТГ", unique=True, null=False, db_index=True
    )
    username = models.CharField(verbose_name="Ник в ТГ", null=True, max_length=50)
    location = models.CharField(
        verbose_name="Указанное местоположение", null=True, blank=True, max_length=100
    )
    phone = models.CharField(verbose_name="Номер телефона", blank=True, max_length=20)
    is_banned = models.BooleanField(
        verbose_name="В бане", default=False, null=False, db_index=True
    )
    is_staff = models.BooleanField(
        verbose_name="Админ", default=False, null=False, db_index=True
    )
    company_name = models.CharField(
        verbose_name="Название компании (СТО)", null=True, max_length=255
    )

    @property
    def get_fullname(self):
        """Возвращает полное имя пользователя, как оно указано в Телеграме."""

        return f"{self.first_name} {self.last_name}".strip()

    def stats_as_tg_html(self):
        rrs = RegisteredRequest.objects.filter(request__user=self).order_by("pk")
        if rrs.count() == 0:
            return None
        rrs_str = ""
        for rr in rrs:
            rrs_str = f"{rrs_str} {rr.as_tg_html()}"
        return (
            f'<a href="tg://user?id={self.user_id}">#{self.pk} {self.name}</a>:'
            f"{rrs_str}"
        )

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

    def subscribed_to_service(self, service):
        active_subs = self.subscriptions.filter(
            service=service,
            expiry_time__gte=now(),
        )
        if active_subs:
            return active_subs[0].expiry_time

        return None


class RepairsType(models.Model):
    """Модель со списком разновидностей категорий заявок."""

    name = models.CharField(verbose_name="Наименование", max_length=255, blank=False)

    def __str__(self):
        return f"#{self.pk} {self.name}"

    @classmethod
    def get_tag_by_name(cls, text):
        return cls.objects.get(name=text)


class WorkRequestStage(models.Model):
    """
    Модель стадии оформления заявки.
    """

    name = models.CharField(
        verbose_name="Наименование", max_length=50, blank=True, default=""
    )
    processor = models.CharField(
        verbose_name="Процессор обработки", max_length=50, null=True
    )
    reply_pattern = models.TextField(verbose_name="Шаблон ответа", null=True)
    buttons = models.JSONField(verbose_name="Набор кнопок", null=True)

    def get_processor(self):
        processors = {
            RequestFormingStage.WELCOME: StartInputProcessor,
            RequestFormingStage.GET_NAME: NameInputProcessor,
            RequestFormingStage.GET_REQUEST_TAG: TagInputProcessor,
            RequestFormingStage.GET_CAR_TYPE: CarTypeInputProcessor,
            RequestFormingStage.GET_DESC: DescriptionInputProcessor,
            RequestFormingStage.REQUEST_PHOTOS: StorePhotoInputProcessor,
            RequestFormingStage.GET_LOCATION: LocationKeyInputProcessor,
            RequestFormingStage.CONFIRM_LOCATION: LocationConfirmationProcessor,
            RequestFormingStage.CHECK_DATA: SetReadyInputProcessor,
            RequestFormingStage.LEAVE_FEEDBACK: FeedbackInputProcessor,
        }
        return processors.get(self.pk)

    def get_by_callback(self, callback):
        callback_to_stage = {
            "new_request": RequestFormingStage.GET_NAME,
            "restart": RequestFormingStage.WELCOME,
            "leave_feedback": RequestFormingStage.LEAVE_FEEDBACK,
        }

        return callback_to_stage.get(callback)


class WorkRequest(
    TrackableUpdateCreateModel, LocationRegionBindModel, CacheableFillDataModel
):
    """
    Модель заявки

    Содержит все введённые пользователем данные, относящиеся к ремонту,
    связь с пользователем и диалогом, флаги состояния и время создания.
    """

    tag = models.ForeignKey(
        RepairsType, on_delete=models.SET_NULL, db_index=True, null=True
    )
    title = models.CharField(
        verbose_name="Наименование задачи", max_length=70, blank=True
    )
    description = models.TextField(
        verbose_name="Подробное описание", max_length=700, blank=True
    )
    user: BotUser = models.ForeignKey(
        BotUser, on_delete=models.CASCADE, db_index=True, related_name="requests"
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
    is_locked = models.BooleanField(
        verbose_name="Флаг полного завершения работы по заявке",
        default=False,
        db_index=True,
    )
    dialog = models.OneToOneField(
        "convoapp.Dialog",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bound_workrequest",
        default=None,
    )
    stage = models.ForeignKey(
        WorkRequestStage, on_delete=models.SET_NULL, null=True, default=1
    )
    # photos backref
    # registered backref

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"#{self.pk} {self.user} {self.tag} {self.is_complete}"

    @property
    def registered(self) -> "RegisteredRequest":
        return self.registered_posts

    @classmethod
    def get_or_create(cls, user, dialog):
        """
        Возвращает заявку, которая привязана к пользователю и диалогу,
        или же формирует новую.
        Заявка считается завершённой, либо если она зарегистрирована,
        либо если отброшена.
        """

        return cls.objects.get_or_create(user=user, dialog=dialog, is_discarded=False)

    # todo separate into a manager?
    def data_as_dict(self):
        """
        Возвращает данные, релевантные для формирования ответов пользователям,
        в виде словаря.
        """

        data_dict = super().data_as_dict()
        if not self._data_dict:
            if self.is_complete:
                post = self.registered
                registered_msg_id = post.channel_message_id
                registered_feedback = post.feedback
            else:
                registered_msg_id = "000"
                registered_feedback = None
            if self.tag:
                tag_name = self.tag.name.replace("/", "_").replace(" ", "_")
            else:
                tag_name = None
            repair_dict = dict(
                request_tag=tag_name,
                registered_msg_id=registered_msg_id,
                registered_feedback=registered_feedback,
            )
            self.set_dict_data(**data_dict)
            self.set_dict_data(**repair_dict)
            self.set_dict_data(**self.location_as_dict())
        return self._data_dict

    def get_media(self):
        """
        Возвращает объект фотографии, пригодный для передачи в Телеграм.

        Либо первое из загруженных фото, либо картинку по умолчанию, если
        фотографии не были загружены.
        """

        if self.photos.all():
            return self.photos.all()[0].tg_file_id
        else:
            return File(open(DEFAULT_LOGO_FILE, "rb"))

    def get_related_tag(self, text):
        try:
            tag = RepairsType.objects.get(name=text)
        except RepairsType.DoesNotExist:
            tag = RepairsType.objects.get(pk=1)  # default "Другое"

        return tag

    def get_reply_for_stage(self):
        """Возвращает шаблон сообщения, соответствующего переданной стадии диалога"""

        num = self.stage_id - 1
        msg = self._fill_data(repair_strings.stages_info[num])
        msg = self._add_location_choices(msg)

        return msg

    def get_feedback_message(self):
        """Возвращает шаблон сообщения для отзыва."""

        msg = self._fill_data(repair_strings.feedback)

        return msg

    def get_admin_message(self):
        """Возвращает шаблон сообщения для администрирования."""

        msg = self._fill_data(repair_strings.admin)

        return msg

    def get_summary(self, ready=False, forward=False):
        """Возвращает шаблон саммари"""

        if not forward:
            msg = self._fill_data(repair_strings.summary)
        else:
            msg = self._fill_data(repair_strings.summary_forward)
        msg["caption"] = msg.pop("text")
        msg["photo"] = self.get_media()
        if ready:
            msg.pop("buttons")

        return msg

    def get_ready_stage(self):
        return RequestFormingStage.DONE

    def check_data(self):
        return self.stage_id == RequestFormingStage.CHECK_DATA

    def is_done(self):
        return self.stage_id in [
            RequestFormingStage.DONE,
            RequestFormingStage.FEEDBACK_DONE,
        ]

    def restart(self):
        self.stage_id = RequestFormingStage.WELCOME

    def get_tg_instance(self):
        return self.dialog.bot.telegram_instance

    def delete_post(self):
        instance = self.get_tg_instance()
        bot = instance.tg_bot
        try:
            bot.delete_message(instance.publish_id, self.registered.channel_message_id)
        except BadRequest:
            pass
        finally:
            self.is_locked = True
            self.save()

    @transaction.atomic
    def set_ready(self):
        """
        Выставляет заявке статус готовности.

        Загружает фотографии в базу данных, ставит отметку в логе, выставляет флаг
        готовности, а затем публикует заявку в канал
        """

        # todo implement a load queue
        bot = self.get_tg_instance().tg_bot
        try:
            for photo in self.photos.all():
                file = bot.get_file(file_id=photo.tg_file_id)
                temp = tempfile.TemporaryFile()
                file.download(out=temp)
                photo.image.save(f"{photo.tg_file_id}.jpg", temp)
                temp.close()
        except TimedOut:
            BOT_LOG.warning(
                f"Timed Out during getting an image file, bot {bot.get_me()},"
                f" user {self.user.user_id}"
            )

        BOT_LOG.debug(
            LogStrings.DIALOG_SET_READY.format(
                user_id=self.user.username,
                request_id=self.pk,
                photos_count=self.photos.count(),
            )
        )
        self.is_complete = True
        self.save()
        RegisteredRequest.publish(self)

    @classmethod
    def setup_jobs(cls, updater):
        pass


class RegisteredRequest(TrackableUpdateCreateModel):
    """
    Модель зарегистрированных заявок

    Содержит связь с заявкой, а также информацию о посте в канале (номер сообщения)
    """

    bound = models.OneToOneField(
        WorkRequest, on_delete=models.CASCADE, related_name="registered_posts"
    )
    channel_message_id = models.PositiveIntegerField(
        verbose_name="Идентификатор сообщения в канале", null=True, db_index=True
    )
    group_message_id = models.PositiveIntegerField(
        verbose_name="Идентификатор сообщения в группе", null=True, db_index=True
    )
    feedback = models.TextField(
        verbose_name="Отзыв пользователя", null=True, max_length=4000
    )
    is_deleted = models.BooleanField(
        verbose_name="Сообщение удалено из канала", default=False, db_index=True
    )

    def __str__(self):
        return f"{self.pk} {self.bound.user} ({self.channel_message_id})"

    def as_tg_html(self):
        channel_name = self.bound.dialog.bot.telegram_instance.publish_name
        return (
            f'<a href="https://t.me/{channel_name}/'
            f'{self.channel_message_id}">#{self.pk}</a>\n'
            f"🚘 {self.bound.car_type}\n{self.bound.tag.name}"
        )

    @classmethod
    @transaction.atomic
    def publish(cls, bound):
        """Публикует сообщение на базе заявки в основной канал,
        сохраняет номер сообщения."""

        from filterapp.models import RepairsFilter

        reg_request = cls.objects.create(
            bound=bound,
        )
        instance = bound.get_tg_instance()
        bound.set_dict_data(
            registered_pk=reg_request.pk,
        )
        message_ids = send_messages_return_ids(
            bound.get_summary(ready=True),
            instance.publish_id,
            instance.bot,
        )
        reg_request.channel_message_id = message_ids[0]
        reg_request.save()
        bound.save()
        bound.set_dict_data(
            registered_msg_id=reg_request.channel_message_id,
        )
        send_messages_return_ids(
            bound.get_admin_message(),
            instance.admin_group_id,
            instance.bot,
        )
        RepairsFilter.trigger_send(reg_request)

    def post_feedback(self):
        """Размещает отзыв в группе отзывов и под сообщением в канале"""

        instance = self.bound.get_tg_instance()
        try:
            send_messages_return_ids(
                self.bound.get_feedback_message(),
                instance.discussion_group_id,
                instance.bot,
                reply_to=self.group_message_id,
            )
        except BadRequest:
            # todo add proper logging
            pass
        send_messages_return_ids(
            self.bound.get_feedback_message(),
            instance.feedback_group_id,
            instance.bot,
        )


class RequestPhoto(models.Model):
    """Модель для хранения сопровождающих фотографий к заявке"""

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


class RequestFormingStage(models.IntegerChoices):
    """Набор стадий проведения диалога."""

    WELCOME = 1, _("Приветствие")
    GET_NAME = 2, _("Получить имя")
    GET_REQUEST_TAG = 3, _("Получить категорию заявки")
    GET_CAR_TYPE = 4, _("Получить тип автомобиля")
    GET_DESC = 5, _("Получить описание заявки")
    REQUEST_PHOTOS = 6, _("Предложить отправить фотографии")
    GET_LOCATION = 7, _("Получить местоположение")
    CONFIRM_LOCATION = 8, _("Подтвердить местоположение")
    CHECK_DATA = 9, _("Проверить заявку")
    DONE = 10, _("Работа завершена")
    LEAVE_FEEDBACK = 11, _("Оставить отзыв")
    FEEDBACK_DONE = 12, _("Отзыв получен")


class Region(models.Model):
    """Модель для описания региона (для разделения локаций)"""

    name = models.CharField(
        verbose_name="Наименование",
        max_length=20,
        blank=False,
        db_index=True,
        unique=True,
    )

    def __str__(self):
        return f"{self.name} #{self.pk}"

    @classmethod
    def get_tag_by_name(cls, text):
        return cls.objects.get(name=text)


class Location(models.Model):
    """Модель локации со всеми её версиями названий"""

    name = models.CharField(
        verbose_name="Наименование",
        max_length=50,
        blank=False,
        db_index=True,
    )
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, db_index=True, related_name="locations"
    )

    def __str__(self):
        return f"{self.name} #{self.pk} ({self.region})"
