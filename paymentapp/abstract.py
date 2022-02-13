from typing import TYPE_CHECKING, Protocol

from django.db import models, transaction

from convoapp.models import Message
from paymentapp.models import Checkout, Order
from subscribeapp.constants import SubTierChoice, ServiceChoice
from subscribeapp.models import Subscription
from tgbot.bot.senders import send_messages_return_ids
from tgbot.bot.utils import get_bot_message_as_text

if TYPE_CHECKING:
    from convoapp.models import Dialog
    from filterapp.models import RepairsFilterStageChoice
    from tgbot.models import BotUser


class BindableProtocol(Protocol):
    @property
    def dialog(self) -> 'Dialog':
        ...

    @property
    def user(self) -> 'BotUser':
        ...

    @property
    def stage_id(self) -> 'RepairsFilterStageChoice':
        ...

    @stage_id.setter
    def stage_id(self, value: 'RepairsFilterStageChoice'):
        ...

    def save(self):
        ...


class SubscribableModel(models.Model):
    """Описывает поведение сервисов, на которые возможна подписка"""

    class Meta:
        abstract = True

    @transaction.atomic
    def make_subscription(self: BindableProtocol, tier=SubTierChoice.MONTH):
        sub = Subscription.get_or_create(self.dialog.user, tier, self.__class__.__name__)
        order = Order.get_or_create(self.dialog, sub)
        checkout = Checkout.get_or_create(order)

        return checkout

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
            self.bound.set_dict_data(
                sub_active="Оформлена",
                # todo fix hardwired repairsbot
                expiry_date=self.user.subscribed_to_service(ServiceChoice.REPAIRS_BOT),
            )
            self.stage_id += 1
            self.save()
