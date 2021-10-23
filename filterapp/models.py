import copy
from datetime import timedelta

from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from abstract.models import TrackableUpdateCreateModel
from bazaarapp.models import SaleAd
from convoapp.processors import SetReadyInputProcessor, StartInputProcessor
from filterapp import strings_bazaar as bazaar_filter_strings
from filterapp.jobs import PlanBroadcast
from filterapp.processors import (
    HighPriceInputProcessor,
    LowPriceInputProcessor,
    RegionMultiSelectProcessor,
    SubCheckProcessor,
)
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.senders import send_messages_return_ids
from tgbot.bot.utils import fill_data
from tgbot.models import BotUser, MessengerBot, Region


class FilterFormingStage(models.IntegerChoices):
    """Набор стадий анкеты фильтра."""

    WELCOME = 1, _("Приветствие")
    CHECK_SUBSCRIPTION = 2, _("Проверка подписки")
    GET_LOW_PRICE = 3, _("Узнать нижнюю границу цены")
    GET_HIGH_PRICE = 4, _("Узнать верхнюю границу цены")
    GET_REGIONS = 5, _("Узнать интересующие регионы")
    CHECK_DATA = 6, _("Проверить данные")
    DONE = 7, _("Фильтр сформирован")


class BazaarFilterStage(models.Model):
    """
    Модель стадии оформления фильтра
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
            FilterFormingStage.WELCOME: StartInputProcessor,
            FilterFormingStage.CHECK_SUBSCRIPTION: SubCheckProcessor,
            FilterFormingStage.GET_LOW_PRICE: LowPriceInputProcessor,
            FilterFormingStage.GET_HIGH_PRICE: HighPriceInputProcessor,
            FilterFormingStage.GET_REGIONS: RegionMultiSelectProcessor,
            FilterFormingStage.CHECK_DATA: SetReadyInputProcessor,
            FilterFormingStage.DONE: None,
        }
        return processors.get(self.pk)

    def get_by_callback(self, callback):
        callback_to_stage = {
            "new_request": FilterFormingStage.CHECK_SUBSCRIPTION,
            "restart": FilterFormingStage.WELCOME,
        }

        return callback_to_stage.get(callback)


class BazaarFilter(TrackableUpdateCreateModel):
    """
    Модель фильтра на базе заполнения анкеты
    """

    user = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="filters",
    )
    low_price = models.PositiveIntegerField(
        verbose_name="Нижний предел цены",
        null=True,
        db_index=True,
    )
    high_price = models.PositiveIntegerField(
        verbose_name="Верхний предел цены",
        null=True,
        db_index=True,
    )
    regions = models.ManyToManyField(Region, verbose_name="Регионы")
    is_complete = models.BooleanField(
        verbose_name="Флаг готовности фильтра", default=False, db_index=True
    )
    is_discarded = models.BooleanField(
        verbose_name="Флаг отказа от формирования фильтра", default=False, db_index=True
    )
    dialog = models.OneToOneField(
        "convoapp.Dialog",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bound_bazaarfilter",
        default=None,
    )
    stage = models.ForeignKey(
        BazaarFilterStage, on_delete=models.SET_NULL, null=True, default=1
    )

    def __str__(self):
        return (
            f"#{self.pk} {self.user} {self.low_price}-{self.high_price} "
            f"{self.regions.all()} {self.is_complete}"
        )

    @classmethod
    def get_or_create(cls, user, dialog):
        """
        Возвращает фильтр, который привязан к пользователю и диалогу,
        или же формирует новый.
        Фильтр считается завершённым, либо если он зарегистрирован,
        либо если отброшен.
        """

        return cls.objects.get_or_create(user=user, dialog=dialog, is_discarded=False)

    @classmethod
    def trigger_send(cls, registered_ad):
        users = BotUser.objects.filter(
            filters__is_complete=True,
            filters__registered__is_active=True,
            filters__low_price__lte=registered_ad.bound.exact_price,
            filters__high_price__gte=registered_ad.bound.exact_price,
            filters__regions=registered_ad.bound.location_key.region,
        ).distinct()
        if users:
            msg_bot = MessengerBot.get_by_model_name(cls.__name__)
            jobs = msg_bot.telegram_instance.job_queue
            msg = registered_ad.bound.get_summary(forward=True)
            jobs.run_once(
                PlanBroadcast(msg_bot, users, msg),
                10,
                name="filter_broadcast",
            )
            BOT_LOG.info(f"Filters triggered, ad #{registered_ad.pk}.")
        else:
            BOT_LOG.info(f"No Filters triggered, ad #{registered_ad.pk}.")

    def data_as_dict(self):
        """
        Возвращает данные, релевантные для формирования ответов пользователям,
        в виде словаря.
        """

        return dict(
            registered_pk=self.registered.pk if self.is_complete else None,
            filter_pk=self.pk,
            channel_name=self.get_tg_instance().publish_name,
            low_price=self.low_price,
            high_price=self.high_price,
            regions=", ".join([r.name for r in self.regions.all()]),
        )

    def get_m2m_choices_as_buttons(self, field_name):
        m2m_model = self._meta.get_field(field_name).related_model
        field = getattr(self, field_name)
        button_flags = [
            (tag.name, tag in field.all()) for tag in m2m_model.objects.all()
        ]
        row_len = 2
        names = [
            dict(text=f"{'☑' if entry[1] else '☐'} {entry[0]}")
            for entry in button_flags
        ]
        buttons = [
            names[i : i + row_len] for i in range(0, len(names), row_len)  # noqa: E203
        ]
        return buttons

    def fill_data(self, message_data: dict) -> dict:
        """Подставляет нужные данные в тело ответа и параметры кнопок."""

        msg = copy.deepcopy(message_data)
        msg["text"] = msg["text"].format(**self.data_as_dict())
        field_name = msg.get("attr_choices")
        if field_name:
            buttons_as_list = self.get_m2m_choices_as_buttons(field_name)
            buttons_as_list.extend(msg.get("text_buttons"))
            msg["text_buttons"] = buttons_as_list
        if msg.get("buttons") or msg.get("text_buttons"):
            for row in msg.get("buttons", []):
                for button in row:
                    for field in button.keys():
                        button[field] = button[field].format(**self.data_as_dict())
            for row in msg.get("text_buttons", []):
                for button in row:
                    for field in button.keys():
                        button[field] = button[field].format(**self.data_as_dict())

        return msg

    def get_reply_for_stage(self):
        """Возвращает шаблон сообщения, соответствующего переданной стадии диалога"""

        num = self.stage_id - 1
        stages_info = bazaar_filter_strings.stages_info[num]

        msg = self.fill_data(stages_info)

        return msg

    def get_summary(self):
        """Возвращает шаблон саммари"""

        msg = fill_data(bazaar_filter_strings.summary, self.data_as_dict())

        return msg

    def get_ready_stage(self):
        return FilterFormingStage.DONE

    def check_data(self):
        return self.stage_id == FilterFormingStage.CHECK_DATA

    def is_done(self):
        return self.stage_id in [
            FilterFormingStage.DONE,
        ]

    def restart(self):
        self.stage_id = FilterFormingStage.WELCOME

    def get_tg_instance(self):
        return self.dialog.bot.telegram_instance

    def get_results(self):
        return SaleAd.objects.filter(
            location_key__region__in=self.regions.all(),
            exact_price__gte=self.low_price,
            exact_price__lte=self.high_price,
            is_complete=True,
            is_locked=False,
            registered_posts__created_at__gt=now() - timedelta(days=3),
            registered_posts__is_deleted=False,
        ).order_by("-created_at")[:10]

    def results_as_text(self, results):
        msg = fill_data(bazaar_filter_strings.results, self.data_as_dict())
        if results:
            results_text = "\n\n".join([r.registered.as_tg_html() for r in results])
        else:
            results_text = "Ничего не найдено."
        msg["text"] = f'{msg.get("text")}\n{results_text}'
        return msg

    @transaction.atomic
    def set_ready(self):
        """
        Выставляет фильтру статус готовности.

        Ставит отметку в логе, выставляет флаг готовности.
        """

        # todo implement a load queue
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_READY.format(
                user_id=self.user.username,
                request_id=self.pk,
                photos_count=None,
            )
        )
        self.is_complete = True
        self.save()
        RegisteredBazaarFilter.activate(self)

    def setup_jobs(self):
        pass


class RegisteredBazaarFilter(TrackableUpdateCreateModel):
    """
    Модель сформированного фильтра
    """

    bound = models.OneToOneField(
        BazaarFilter, on_delete=models.CASCADE, related_name="registered"
    )
    is_active = models.BooleanField(verbose_name="Фильтр задействован", default=True)

    @classmethod
    @transaction.atomic
    def activate(cls, bound):
        cls.objects.filter(is_active=True).update(is_active=False)
        cls.objects.create(bound=bound)
        instance = bound.get_tg_instance()
        results = bound.get_results()

        send_messages_return_ids(
            bound.results_as_text(results),
            bound.user.user_id,
            instance.bot,
        )
