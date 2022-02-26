from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.timezone import now
from djmoney.money import Money

from abstract.models import TrackableUpdateCreateModel
from subscribeapp.constants import ServiceChoice, SubTierChoice
from tgbot.models import BotUser


class Subscription(TrackableUpdateCreateModel):

    user = models.ForeignKey(
        BotUser,
        verbose_name="Пользователь",
        on_delete=models.RESTRICT,
        db_index=True,
        related_name="subscriptions",
    )
    tier = models.PositiveSmallIntegerField(
        verbose_name="Уровень подписки", choices=SubTierChoice.choices
    )
    service = models.PositiveSmallIntegerField(
        verbose_name="Сервис, на который оформлена подписка",
        choices=ServiceChoice.choices,
    )
    is_active = models.BooleanField(
        verbose_name="Подписка активна", default=False, db_index=True
    )
    start_time = models.DateTimeField(
        verbose_name="Время начала подписки",
        db_index=True,
        null=True,
    )
    expiry_time = models.DateTimeField(
        verbose_name="Время окончания подписки",
        db_index=True,
        null=True,
    )

    @classmethod
    def get_or_create(cls, user, tier, service: int) -> "Subscription":

        obj, created = cls.objects.get_or_create(
            user=user,
            tier=tier,
            service=service,
            is_active=False,
        )

        return obj

    @classmethod
    def get_active(cls, user, service: int) -> "Subscription":

        obj = cls.objects.get(
            user=user,
            service=service,
            is_active=True,
        )

        return obj

    def get_price(self):
        price_dict = {
            SubTierChoice.MONTH.value: Money(10, "UAH"),
            SubTierChoice.YEAR.value: Money(100, "UAH"),
            SubTierChoice.FOREVER.value: Money(200, "UAH"),
        }

        return price_dict.get(self.tier)

    def notify_user(self):
        self.order.dialog.bound.send_payment_confirmation()

    def activate(self):
        # todo continue HERE

        tiers_dict = {
            SubTierChoice.MONTH: relativedelta(months=1),
            SubTierChoice.YEAR: relativedelta(years=1),
            SubTierChoice.FOREVER: relativedelta(years=100),
        }
        delta = tiers_dict.get(self.tier)

        self.start_time = now()
        self.expiry_time = now() + delta
        self.is_active = True
        self.save()

    def is_expired(self):
        if self.expiry_time:
            return self.expiry_time < now()
        return True
