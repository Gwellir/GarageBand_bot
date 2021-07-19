from convoapp.processors import TextInputProcessor
from tgbot.exceptions import IncorrectNumberError, NotANumberError, TextNotProvidedError


class PriceTagInputProcessor(TextInputProcessor):
    """Процессор ввода типа ремонта.

    Получает из БД соответствующий вводу пользователя тег и сохраняет его
    в заявку.
    """

    attr_name = "price_tag"

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        text = data["text"]
        return self.model.get_related_tag(text)


class PriceInputProcessor(TextInputProcessor):
    """Процессор ввода цены с форматом валюты"""

    attr_name = "exact_price"


class MileageInputProcessor(TextInputProcessor):
    """Обработчик ввода километража."""

    attr_name = "mileage"

    def get_field_value(self, data):
        if not data["text"] or data["callback"]:
            raise TextNotProvidedError
        text = data.get("text")
        try:
            num = int(text)
        except ValueError:
            raise NotANumberError
        if num < 0:
            raise IncorrectNumberError
        return num
