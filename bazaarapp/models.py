from datetime import datetime, timedelta
from time import sleep

from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from telegram import InputMediaPhoto, ParseMode
from telegram.error import BadRequest, TimedOut

from abstract.models import (
    CacheableFillDataModel,
    LocationRegionBindModel,
    TrackableUpdateCreateModel,
)
from bazaarapp import strings as bazaar_strings
from bazaarapp.jobs import ReminderJob
from bazaarapp.processors import (
    AlbumPhotoProcessor,
    BargainSelectProcessor,
    LocationConfirmationProcessor,
    LocationKeyInputProcessor,
    MileageInputProcessor,
    PriceInputProcessor,
    SetCompleteInputProcessor,
)
from convoapp.processors import (
    CarTypeInputProcessor,
    DescriptionInputProcessor,
    NameInputProcessor,
    PhoneNumberInputProcessor,
    SetReadyInputProcessor,
    StartInputProcessor,
)
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.constants import (
    BAZAAR_REMINDER_TIME,
    DEFAULT_AD_LOGO_FILE,
    DEFAULT_AD_SOLD_FILE,
)
from tgbot.bot.senders import send_messages_return_ids
from tgbot.exceptions import IncorrectChoiceError
from tgbot.models import BotUser


class AdFormingStage(models.IntegerChoices):
    """Набор стадий проведения диалога."""

    WELCOME = 1, _("Приветствие")
    GET_NAME = 2, _("Получить имя")
    GET_PHONE = 3, _("Получить телефон")
    GET_CAR_TYPE = 4, _("Получить тип автомобиля")
    GET_CAR_MILEAGE = 5, _("Получить пробег автомобиля")
    GET_EXACT_PRICE = 6, _("Получить точную цену")
    GET_BARGAIN = 7, _("Узнать возможность торга ")
    GET_DESC = 8, _("Получить описание объявления")
    REQUEST_PHOTOS = 9, _("Предложить отправить фотографии")
    GET_LOCATION = 10, _("Получить местоположение")
    CONFIRM_LOCATION = 11, _("Подтвердить местоположение")
    CHECK_DATA = 12, _("Проверить заявку")
    DONE = 13, _("Работа завершена")
    SALE_COMPLETE = 14, _("Заявка закрыта")


class PriceTag(models.Model):
    """Модель со списком разновидностей ценовых категорий заявок."""

    name = models.CharField(verbose_name="Наименование", max_length=255, blank=False)
    short_name = models.CharField(verbose_name="Краткое наименование", max_length=20)
    low = models.PositiveIntegerField(verbose_name="Нижняя граница цены", null=True)
    high = models.PositiveIntegerField(verbose_name="Верхняя граница цены", null=True)

    def __str__(self):
        return f"#{self.pk} {self.name}"

    @classmethod
    def get_by_price(cls, price: int) -> "PriceTag":
        return cls.objects.get(
            Q(low__lte=price) | Q(low=None), Q(high__gte=price) | Q(high=None)
        )

    @classmethod
    def get_tag_by_name(cls, text):
        return cls.objects.get(name=text)


class SaleAdStage(models.Model):
    """
    Модель стадии оформления объявления.
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
            AdFormingStage.WELCOME: StartInputProcessor,
            AdFormingStage.GET_NAME: NameInputProcessor,
            AdFormingStage.GET_PHONE: PhoneNumberInputProcessor,
            AdFormingStage.GET_CAR_TYPE: CarTypeInputProcessor,
            AdFormingStage.GET_CAR_MILEAGE: MileageInputProcessor,
            AdFormingStage.GET_EXACT_PRICE: PriceInputProcessor,
            AdFormingStage.GET_BARGAIN: BargainSelectProcessor,
            AdFormingStage.GET_DESC: DescriptionInputProcessor,
            AdFormingStage.REQUEST_PHOTOS: AlbumPhotoProcessor,
            AdFormingStage.GET_LOCATION: LocationKeyInputProcessor,
            AdFormingStage.CONFIRM_LOCATION: LocationConfirmationProcessor,
            AdFormingStage.CHECK_DATA: SetReadyInputProcessor,
            AdFormingStage.DONE: SetCompleteInputProcessor,
        }
        return processors.get(self.pk)

    def get_by_callback(self, callback):
        callback_to_stage = {
            "new_request": AdFormingStage.GET_NAME,
            "restart": AdFormingStage.WELCOME,
        }

        return callback_to_stage.get(callback)


class SaleAd(
    TrackableUpdateCreateModel, LocationRegionBindModel, CacheableFillDataModel
):
    """
    Модель заявки

    Содержит все введённые пользователем данные, относящиеся к ремонту,
    связь с пользователем и диалогом, флаги состояния и время создания.
    """

    price_tag = models.ForeignKey(
        PriceTag, on_delete=models.SET_NULL, db_index=True, null=True
    )
    exact_price = models.PositiveIntegerField(verbose_name="Цена", null=True)
    can_bargain = models.BooleanField(verbose_name="Торг возможен", null=True)
    mileage = models.PositiveIntegerField(verbose_name="Пробег", null=True)
    description = models.TextField(
        verbose_name="Подробное описание", max_length=750, blank=True
    )
    user: BotUser = models.ForeignKey(
        BotUser, on_delete=models.CASCADE, db_index=True, related_name="ads"
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
        verbose_name="Флаг завершения продажи", default=False, db_index=True
    )
    dialog = models.OneToOneField(
        "convoapp.Dialog",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bound_salead",
        default=None,
    )
    stage = models.ForeignKey(
        SaleAdStage, on_delete=models.SET_NULL, null=True, default=1
    )
    # photos backref
    # registered_posts backref

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"#{self.pk} {self.user} {self.price_tag} {self.is_complete}"

    @property
    def registered(self) -> "RegisteredAd":
        return self.registered_posts.get(is_deleted=False)

    @classmethod
    def get_or_create(cls, user, dialog):
        """
        Возвращает заявку, которая привязана к пользователю и диалогу,
        или же формирует новую.
        Заявка считается завершённой, либо если она зарегистрирована,
        либо если отброшена.
        """

        return cls.objects.get_or_create(user=user, dialog=dialog, is_discarded=False)

    def set_dict_data(self, **kwargs):
        for key, value in kwargs.items():
            self._data_dict[key] = value

    # todo separate into a manager?
    def data_as_dict(self):
        """
        Возвращает данные, релевантные для формирования ответов пользователям,
        в виде словаря.
        """

        data_dict = super().data_as_dict()
        if not self._data_dict:
            registered_feedback = tag_name = None
            if self.is_complete:
                post = self.registered
                registered_msg_id = post.channel_message_id
                registered_feedback = post.feedback
            else:
                registered_msg_id = "000"
            if self.can_bargain:
                ad_bargain_string = "Торг!"
            else:
                ad_bargain_string = ""
            if self.price_tag:
                tag_name = self.price_tag.name.replace("$", "").replace(" ", "_")
            if self.photos.count():
                photos_loaded = "<pre>Фотографии загружены</pre>\n"
            else:
                photos_loaded = ""
            bazaar_data = dict(
                ad_price_range=tag_name,  #
                ad_mileage=self.mileage,  #
                ad_price=self.exact_price,  #
                ad_bargain_string=ad_bargain_string,  #
                photos_loaded=photos_loaded,  #
                registered_msg_id=registered_msg_id,  #
                registered_feedback=registered_feedback,  #
            )
            self.set_dict_data(**data_dict)
            self.set_dict_data(**bazaar_data)
            self.set_dict_data(**self.location_as_dict())
        return self._data_dict

    def _get_media(self):
        """
        Возвращает объект фотографии, пригодный для передачи в Телеграм.

        Либо первое из загруженных фото, либо картинку по умолчанию, если
        фотографии не были загружены.
        """

        if self.photos.all():
            return [
                InputMediaPhoto(photo.tg_file_id) for photo in self.photos.all()[:9]
            ]
        else:
            return []

    def post_media(self):
        album = self._get_media()[1:]
        instance = self.get_tg_instance()
        bot = instance.tg_bot
        if len(album) > 1:
            bot.send_media_group(
                chat_id=instance.discussion_group_id,
                media=album,
                reply_to_message_id=self.registered.group_message_id,
            )
        elif len(album):
            bot.send_photo(
                photo=album[0].media,
                chat_id=instance.discussion_group_id,
                reply_to_message_id=self.registered.group_message_id,
            )

    def get_related_tag(self, text):
        try:
            tag = PriceTag.objects.get(name=text)
        except PriceTag.DoesNotExist:
            raise IncorrectChoiceError(text)

        return tag

    def get_tag_by_price(self, price: int) -> PriceTag:
        try:
            tag = PriceTag.get_by_price(price)
        except PriceTag.DoesNotExist:
            raise IncorrectChoiceError(price)

        return tag

    def get_reply_for_stage(self):
        """Возвращает шаблон сообщения, соответствующего переданной стадии диалога"""

        num = self.stage_id - 1
        msg = self._fill_data(bazaar_strings.stages_info[num])
        msg = self._add_location_choices(msg)

        return msg

    def get_feedback_message(self):
        """Возвращает шаблон сообщения для отзыва."""

        msg = self._fill_data(bazaar_strings.feedback)

        return msg

    def get_admin_message(self):
        """Возвращает шаблон сообщения для администрирования."""

        msg = self._fill_data(bazaar_strings.admin)

        return msg

    def get_summary(self, ready=False, forward=False):
        """Возвращает шаблон саммари"""

        media = self._get_media()
        if not forward:
            msg = self._fill_data(bazaar_strings.summary)
        else:
            msg = self._fill_data(bazaar_strings.summary_forward)
        msg["caption"] = msg.pop("text")
        if media:
            msg["photo"] = media[0].media
        else:
            msg["photo"] = InputMediaPhoto(open(DEFAULT_AD_LOGO_FILE, "rb")).media
        msg["ready"] = ready
        if ready:
            msg.pop("buttons")

        return msg

    def get_summary_sold(self):
        msg = self._fill_data(bazaar_strings.summary_sold)
        return msg["text"]

    def get_renewal(self):
        msg = self._fill_data(bazaar_strings.renewal)
        return msg

    def get_ready_stage(self):
        return AdFormingStage.DONE

    def check_data(self):
        return self.stage_id == AdFormingStage.CHECK_DATA

    def is_done(self):
        return self.stage_id in [
            AdFormingStage.DONE,
            AdFormingStage.SALE_COMPLETE,
        ]

    def restart(self):
        self.stage_id = AdFormingStage.WELCOME

    def get_tg_instance(self):
        return self.dialog.bot.telegram_instance

    def delete_post(self):
        instance = self.get_tg_instance()
        bot = instance.tg_bot
        try:
            bot.delete_message(instance.publish_id, self.registered.channel_message_id)
            if self.registered.album_start_id:
                for msg_id in range(
                    self.registered.album_start_id, self.registered.album_end_id + 1
                ):
                    bot.delete_message(instance.publish_id, msg_id)
        except BadRequest as e:
            print(e)
        finally:
            self._lock_post()

    def _lock_post(self):
        self.is_locked = True
        post: RegisteredAd = self.registered
        post.is_deleted = True
        post.save()
        self.save()

    @transaction.atomic
    def set_sold(self):
        """
        Выставляет объявлению статус завершения.

        Выставляет флаг блокировки, заменяет фотографии в канале на "ПРОДАНО"
        """

        self.is_locked = True
        self.save()
        instance = self.get_tg_instance()
        bot = instance.tg_bot
        try:
            bot.edit_message_media(
                chat_id=instance.publish_id,
                message_id=self.registered.channel_message_id,
                media=InputMediaPhoto(open(DEFAULT_AD_SOLD_FILE, "rb")),
            )
            sleep(2)
            bot.edit_message_caption(
                chat_id=instance.publish_id,
                message_id=self.registered.channel_message_id,
                parse_mode=ParseMode.HTML,
                caption=self.get_summary_sold(),
            )
            sleep(2)
        except (TimedOut, BadRequest):
            pass

        BOT_LOG.debug(
            LogStrings.DIALOG_SET_SOLD.format(
                user_id=self.user.username,
                request_id=self.pk,
            )
        )

    def _save_photos(self, bot):
        pass
        # for photo in self.photos.all():
        #     file = bot.get_file(file_id=photo.tg_file_id)
        #     temp = tempfile.TemporaryFile()
        #     file.download(out=temp)
        #     photo.image.save(f"{photo.tg_file_id}.jpg", temp)
        #     temp.close()

    @transaction.atomic
    def set_ready(self):
        """
        Выставляет заявке статус готовности.

        Загружает фотографии в базу данных, ставит отметку в логе, выставляет флаг
        готовности, а затем публикует заявку в канал
        """

        bot = self.get_tg_instance().tg_bot
        self._save_photos(bot)
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_READY.format(
                user_id=self.user.username,
                request_id=self.pk,
                photos_count=self.photos.count(),
            )
        )
        self.is_complete = True
        self.save()
        RegisteredAd.publish(self)

    @classmethod
    def setup_jobs(cls, updater):
        jobs = updater.job_queue
        reminder_time = datetime.strptime(BAZAAR_REMINDER_TIME, "%H:%M:%S %z").time()
        filters = [
            dict(
                before=timedelta(days=21),
                after=timedelta(days=22),
                is_locked=False,
                registered_posts__is_deleted=False,
            ),
        ]
        jobs.run_daily(
            ReminderJob(cls, updater, filters),
            reminder_time,
            name="cleanup",
        )


class RegisteredAd(TrackableUpdateCreateModel):
    """
    Модель зарегистрированных объявлений

    Содержит связь с объявлением, а также информацию о посте в канале (номер сообщения)
    """

    bound: SaleAd = models.ForeignKey(
        SaleAd, on_delete=models.CASCADE, related_name="registered_posts"
    )
    album_start_id = models.PositiveIntegerField(
        verbose_name="Первое сообщение в альбоме", null=True
    )
    album_end_id = models.PositiveIntegerField(
        verbose_name="Последнее сообщение в альбоме", null=True
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
        channel_name = self.bound.get_tg_instance().publish_name
        return (
            f'<a href="https://t.me/{channel_name}/'
            f'{self.channel_message_id}">#{self.pk}</a>\n'
            f"🚘 {self.bound.car_type}\n💸 ${self.bound.exact_price}"
        )

    @classmethod
    @transaction.atomic
    def publish(cls, bound):
        """Публикует сообщение на базе заявки в основной канал,
        сохраняет номер сообщения."""

        from filterapp.bazaar.models import BazaarFilter

        reg_ad = cls.objects.create(
            bound=bound,
        )
        instance = bound.get_tg_instance()
        bound.set_dict_data(
            registered_pk=reg_ad.pk,
        )
        message_ids = send_messages_return_ids(
            bound.get_summary(ready=True),
            instance.publish_id,
            instance.bot,
        )
        reg_ad.channel_message_id = message_ids[0]
        reg_ad.save()
        bound.save()
        bound.set_dict_data(
            registered_msg_id=reg_ad.channel_message_id,
        )
        sleep(1)
        send_messages_return_ids(
            bound.get_admin_message(),
            instance.admin_group_id,
            instance.bot,
        )
        BazaarFilter.trigger_send(reg_ad)

    def repost(self):
        bound = self.bound
        self.is_deleted = True
        self.save()
        RegisteredAd.publish(bound)

    def propose_renewal(self):
        instance = self.bound.get_tg_instance()
        send_messages_return_ids(
            self.bound.get_renewal(),
            self.bound.user.user_id,
            instance.bot,
        )


class AdPhoto(models.Model):
    """Модель для хранения сопровождающих фотографий к объявлению"""

    description = models.CharField(
        verbose_name="Описание фото", max_length=255, null=True
    )
    tg_file_id = models.CharField(
        verbose_name="ID файла в ТГ", max_length=255, blank=False
    )
    image = models.ImageField(verbose_name="Фотография", upload_to="user_photos")
    ad = models.ForeignKey(
        SaleAd, on_delete=models.CASCADE, related_name="photos", db_index=True
    )
