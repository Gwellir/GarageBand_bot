from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatusChoice(models.IntegerChoices):
    NEW = 1, _("Сформирован")
    PENDING_PAYMENT = 2, _("Ожидает оплаты")
    PROCESSING = 3, _("Обрабатывается")
    COMPLETE = 4, _("Готов")
    CLOSED = 5, _("Закрыт")
    CANCELED = 6, _("Отменён")
    ON_HOLD = 7, _("Подвешен")
    PAYMENT_REVIEW = 8, _("Оплата проходит ревью")


class PaymentSystemChoice(models.IntegerChoices):
    TELEGRAM = 0, _("Телеграм")
    LIQPAY = 1, _("ЛикПей")