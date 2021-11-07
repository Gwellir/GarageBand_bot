from django.db import models


class SubTierChoice(models.IntegerChoices):
    """Набор уровней подписки"""

    


class Subscription(models.Model):

    user
    tier = models.PositiveSmallIntegerField(verbose_name="Уровень подписки", choices=SubTiers.choices)
    expiry_date = models.DateTimeField(verbose_name="Время окончания подписки", db_index=True)