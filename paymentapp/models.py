from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from abstract.models import TrackableUpdateCreateModel
from tgbot.models import BotUser


class SubTierChoice(models.IntegerChoices):
    """Набор уровней подписки"""

    MONTH = 1, _("Месячная")
    YEAR = 2, _("Годовая")
    FOREVER = 3, _("Навсегда")


class ServiceChoice(models.IntegerChoices):
    """Набор сервисов для оформления подписки"""

    REPAIRS_BOT = 1, _("Бот фильтров автосервиса")
    BAZAAR_BOT = 2, _("Бот фильтров автобазара")


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
    expiry_time = models.DateTimeField(
        verbose_name="Время окончания подписки", db_index=True, default=now
    )

    @classmethod
    def create(cls, user, tier, service):
        tiers_dict = {
            SubTierChoice.MONTH: relativedelta(months=1),
            SubTierChoice.YEAR: relativedelta(years=1),
            SubTierChoice.FOREVER: relativedelta(years=100),
        }
        delta = tiers_dict.get(tier)
        obj, created = cls.objects.get_or_create(
            user=user,
            tier=tier,
            service=service,
        )

        obj.expiry_time += delta
        obj.save()

        return obj

    def is_expired(self):
        return self.expiry_time < now()
