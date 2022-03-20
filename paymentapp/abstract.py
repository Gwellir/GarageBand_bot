from django.db import models, transaction

from abstract.protocols import BindableProtocol
from convoapp.models import Message
from paymentapp.models import Checkout, Order
from subscribeapp.constants import ServiceChoice, SubTierChoice
from subscribeapp.models import Subscription
from tgbot.bot.senders import send_messages_return_ids
from tgbot.bot.utils import get_bot_message_as_text


class SubscribableModel(models.Model):
    """Описывает поведение сервисов, на которые возможна подписка"""

    class Meta:
        abstract = True

    def has_never_subbed(self: BindableProtocol):
        subs = Subscription.objects.filter(
            user=self.dialog.user,
            service=self.get_service_name(),
        )
        return not subs

    @transaction.atomic
    def make_subscription(self: BindableProtocol, tier=SubTierChoice.MONTH, free=False):
        sub = Subscription.get_or_create(
            self.dialog.user, tier, self.get_service_name()
        )
        if free:
            sub.activate()
            return
        order = Order.get_or_create(self.dialog, sub)
        checkout = Checkout.get_or_create(order)

        return checkout

    # todo make this a proper factory
    def get_service_name(self):
        return dict(
            repairsfilter=ServiceChoice.REPAIRS_BOT,
            bazaarfilter=ServiceChoice.BAZAAR_BOT,
        ).get(self.__class__.__name__.lower())

    def _get_payment_confirmation_reply(self):
        pass

    def send_payment_confirmation(self: BindableProtocol):
        """Отправляет пользователю подтверждение о приёме оплаты"""

        msg = self.get_payment_confirmation_reply()
        ids = send_messages_return_ids(msg, self.user.user_id, self.dialog.bot)
        Message.objects.create(
            dialog=self.dialog,
            stage=self.stage_id,
            message_id=ids[0],
            text=get_bot_message_as_text(msg),
            is_incoming=False,
        )
        if not self.dialog.is_finished:
            self.set_dict_data(
                sub_active="Оформлена",
                expiry_date=self.user.subscribed_to_service(self.get_service_name()),
            )
            self.stage_id += 1
            self.save()

    def send_payment_denied(self: BindableProtocol):
        msg = self.get_payments_denied_reply()
        ids = send_messages_return_ids(msg, self.user.user_id, self.dialog.bot)
        Message.objects.create(
            dialog=self.dialog,
            stage=self.stage_id,
            message_id=ids[0],
            text=get_bot_message_as_text(msg),
            is_incoming=False,
        )
        if not self.dialog.is_finished:
            self.stage_id -= 1
            self.save()
