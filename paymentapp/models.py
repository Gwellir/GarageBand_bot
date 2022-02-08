from django.db import models
from django.utils.timezone import now
from djmoney.models.fields import MoneyField

from abstract.models import TrackableUpdateCreateModel
from convoapp.models import Dialog
from paymentapp.constants import OrderStatusChoice, PaymentSystemChoice
from paymentapp.systems.liqpay_system import LiqpayClient
from tgbot.models import BotUser


class OrderItem(TrackableUpdateCreateModel):
    """Модель для описания продукта.

    Содержит поля наименования, цены, описания, категории, ссылки на изображение
    а также активности.
    """

    # item =
    name = models.CharField('Name', max_length=100, db_index=True)
    price = MoneyField('Price', max_digits=10, decimal_places=2, blank=True, default=0.0, default_currency='UAH')
    description = models.TextField('Description', blank=True, default='')
    is_active = models.BooleanField('Active', default=True)
    # objects = OrderItemManager()

    def get_categories(self) -> str:
        return ', '.join(self.categories.values_list('name', flat=True))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
        app_label = 'paymentapp'
        ordering = ['name']


class Checkout(TrackableUpdateCreateModel):

    order = models.ForeignKey(
        'Order',
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="checkouts",
    )
    system = models.IntegerField(
        verbose_name='Billing system',
        choices=PaymentSystemChoice.choices,
        default=PaymentSystemChoice.LIQPAY
    )
    tracking_id = models.CharField(verbose_name='Tracking id', max_length=255, db_index=True)
    system_id = models.CharField(verbose_name='System tracking id', max_length=255, null=True)
    link = models.URLField(verbose_name='Payment link', null=True, blank=True, max_length=1000)
    capture_id = models.CharField('Capture id', max_length=255, null=True, blank=True)
    status = models.CharField(
        "Status", max_length=100, null=True, blank=True, db_index=True
    )

    class Meta:
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'
        app_label = 'paymentapp'
        ordering = ['-created_at']

    @classmethod
    def get_or_create(cls, order: 'Order', system=PaymentSystemChoice.LIQPAY):
        try:
            obj = cls.objects.get(order=order, system=system, status="NEW")
        except cls.DoesNotExist:
            lqp = LiqpayClient()
            link, tracking_id = lqp.check_out(order.total, order.description, order.pk)
            obj = cls.objects.get_or_create(
                order=order,
                system=system,
                status="NEW",
                tracking_id=tracking_id,
                link=link
            )

        return obj

    def set_complete(self):
        self.status = "COMPLETE"
        self.order.set_complete()
        self.save()

    def set_incomplete(self, status: str):
        self.status = status
        self.save()


class Order(TrackableUpdateCreateModel):

    user = models.ForeignKey(
        BotUser,
        verbose_name="Пользователь",
        on_delete=models.RESTRICT,
        db_index=True,
        related_name="orders",
    )
    dialog = models.OneToOneField(
        Dialog,
        verbose_name="Разговор",
        on_delete=models.RESTRICT,
        db_index=True,
        related_name="order",
    )
    description = models.TextField('Comment', default='')
    subscription = models.OneToOneField(
        "subscribeapp.Subscription",
        verbose_name='Subscription to a service',
        on_delete=models.CASCADE,
        null=True,
        related_name="order",
    )
    order_item = models.ForeignKey(OrderItem, verbose_name='OrderItem', on_delete=models.CASCADE, null=True)
    total = MoneyField('Total', max_digits=10, decimal_places=2)

    status = models.IntegerField('Status', choices=OrderStatusChoice.choices, default=OrderStatusChoice.NEW)
    paid_date = models.DateTimeField('Paid date', null=True, blank=True)
    cancel_date = models.DateTimeField('Cancel date', null=True, blank=True)
    # objects = OrderManager()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        app_label = 'paymentapp'
        ordering = ['-created_at']

    @classmethod
    def get_or_create(cls, dialog: 'Dialog', subscription):
        obj, created = cls.objects.get_or_create(
            dialog=dialog,
            user=dialog.user,
            subscription=subscription,
            description=f'Sub: {subscription.tier} for #{dialog.user.pk}',
            total=subscription.get_price()
        )

        return obj

    def set_complete(self):
        if self.subscription and not self.subscription.is_active:
            self.subscription.activate()
        self.status = OrderStatusChoice.COMPLETE
        self.paid_date = now()
        self.save()

    def get_last_checkout(self):
        checkout = self.checkouts.get(status="NEW")
        return checkout
