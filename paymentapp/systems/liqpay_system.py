import uuid
from pprint import pprint
from typing import Tuple

from djmoney.money import Money
from liqpay import LiqPay

from garage_band_bot import settings
from paymentapp.systems.constants import LiqPayResponseFields, LiqPayResponseStatus


class LiqpayClient:
    """Содержит реализацию клиента платёжной системы для LIQPAY"""

    def __init__(self):
        self.liqpay = LiqPay(settings.LQ_TEST_PUBLIC_KEY, settings.LQ_TEST_PRIVATE_KEY)

    def check_out(self, money: Money, desc: str, order_id: int) -> Tuple[str, str]:
        """Создаёт liqpay checkout на базе локального заказа"""

        order_id = f"order_id_{uuid.uuid4().fields[-1]}_{order_id}"
        res: str = self.liqpay.checkout_url(
            dict(
                action="auth",
                version="3",
                amount=str(money.amount),
                currency=str(money.currency),
                description=desc,
                order_id=order_id,
                language="ru",
                recurringbytoken="1",
            )
        )
        pprint(res)

        return res, order_id

    def verify(self, data, signature):
        """Выполняет проверку подлинности ответа liqpay"""

        sign = self.liqpay.str_to_sign(
            settings.LQ_TEST_PRIVATE_KEY + data + settings.LQ_TEST_PRIVATE_KEY
        )

        if sign == signature:
            return True
        return False

    def process(self, data: dict):
        """Проверяет статус ответа и выполняет соответствующие действия
        c внутренним checkout.
        """

        response = self.liqpay.decode_data_from_str(data)
        print("callback data", response)
        status = response.get(LiqPayResponseFields.STATUS)

        from paymentapp.models import Checkout

        order_id = response.get(LiqPayResponseFields.ORDER_ID)
        system_order_id = response.get(LiqPayResponseFields.SYSTEM_ORDER_ID)
        checkout = Checkout.objects.get(tracking_id=order_id)
        checkout.system_id = system_order_id

        if status == LiqPayResponseStatus.SUCCESS:
            checkout.set_complete()
        else:
            checkout.set_incomplete(status)
