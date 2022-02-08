from django.db import models
from django.utils.translation import gettext_lazy as _


class SubTierChoice(models.IntegerChoices):
    """Набор уровней подписки"""

    MONTH = 1, _("Месячная")
    YEAR = 2, _("Годовая")
    FOREVER = 3, _("Навсегда")


class ServiceChoice(models.IntegerChoices):
    """Набор сервисов для оформления подписки"""

    REPAIRS_BOT = 1, _("Бот фильтров автосервиса")
    BAZAAR_BOT = 2, _("Бот фильтров автобазара")