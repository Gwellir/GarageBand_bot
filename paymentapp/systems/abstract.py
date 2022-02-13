from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from django.http import HttpRequest


class PaymentSystemClient(ABC):
    """Абстрактный интерфейс, описывающий поведение платёжной системы."""

    @abstractmethod
    def check_out(self, order_id: int, product_id: int) -> str:
        pass

    @abstractmethod
    def verify(self, request: "HttpRequest") -> bool:
        pass

    @abstractmethod
    def capture(self, wh_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def fulfill(self, data: Dict[str, Any]) -> None:
        pass
