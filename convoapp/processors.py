"""Процессоры данных из ввода пользователя."""

import re

from django.utils.html import strip_tags

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.exceptions import (
    ButtonIsLockedError,
    CallbackNotProvidedError,
    ImageNotProvidedError,
    PhoneNumberMalformedError,
    TextNotProvidedError,
    TextTooLongError,
    TextTooShortError,
)


class BaseInputProcessor:
    """Базовый класс процессора пользовательского ввода.

    Либо устанавливает значение поля, либо обрабатывает нажатие кнопки Отменить
    Возвращает изменение номера стадии диалога после проведения операции."""

    attr_name = None

    def __call__(self, dialog, data):
        self.dialog = dialog
        self.model = dialog.bound
        self.messages = []
        step = self.get_step(data)
        if step > 0:
            self.set_field(data)

        self.dialog.bound.stage_id += step
        return step

    def set_field(self, data):
        pass

    def get_step(self, data):
        if data["text"] == "Отменить":
            return -1
        else:
            return 1


class StartInputProcessor(BaseInputProcessor):
    """Процессор сообщения-приглашения."""

    def get_step(self, data):
        if data["callback"] == "new_request":
            return 1
        return 0


class TextInputProcessor(BaseInputProcessor):
    """Обработчик текстовых данных от пользователя.

    Проверяет соответствие текстовых данных формату, предобрабатывает их,
    формирует объект, который нужно передать в поле модели.
    Сохраняет модель."""

    min_length = 3

    def check_text_length(self, text):
        text_length = len(text)
        max_length = self.model._meta.get_field(self.attr_name).max_length
        if text_length < self.min_length:
            raise TextTooShortError(self.min_length, text_length)
        elif text_length > max_length:
            raise TextTooLongError(max_length, text_length)
        else:
            return True

    def get_field_value(self, data):
        if not data["text"] or data["callback"]:
            raise TextNotProvidedError
        text = data.get("text")
        if self.check_text_length(text):
            return strip_tags(text)

    def set_field(self, raw_text):
        value = self.get_field_value(raw_text)
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.dialog.user.username,
                stage=self.dialog.bound.stage,
                model=self.model,
                data=value,
            )
        )
        setattr(self.model, self.attr_name, value)
        self.model.save()


class NameInputProcessor(TextInputProcessor):
    """Процессор ввода имени (сохраняет имя в модели пользователя)."""

    attr_name = "name"
    min_length = 2

    def set_field(self, data):
        self.model = self.dialog.user
        super().set_field(data)


class TagInputProcessor(TextInputProcessor):
    """Процессор ввода типа ремонта.

    Получает из БД соответствующий вводу пользователя тег и сохраняет его
    в заявку.
    """

    attr_name = "tag"

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        text = data["text"]
        return self.model.get_related_tag(text)


class CarTypeInputProcessor(TextInputProcessor):
    """Процессор ввода типа авто"""

    attr_name = "car_type"


class DescriptionInputProcessor(TextInputProcessor):
    """Процессор ввода описания заявки"""

    attr_name = "description"


class LocationInputProcessor(TextInputProcessor):
    """
    Процессор ввода района, рядом с которым пользователь хотел бы провести работы.
    """

    attr_name = "location"


# todo move validation to the model
class PhoneNumberInputProcessor(TextInputProcessor):
    """Процессор ввода номера телефона.

    Удаляет всё доп. форматирование, кроме стартового плюса (если он есть).
    Выполняет проверку длины номера."""

    attr_name = "phone"

    def set_field(self, data):
        self.model = self.dialog.user
        super().set_field(data)

    def get_field_value(self, data):
        text = super().get_field_value(data)
        cleaned_text = re.sub(r"[^+0-9]", "", text)
        if not (7 < len(cleaned_text) < 15) or cleaned_text.find("+", 1) >= 0:
            raise PhoneNumberMalformedError
        return cleaned_text


class StorePhotoInputProcessor(BaseInputProcessor):
    """Процессор ввода загруженной фотографии.

    Проверяет, не пропускается ли этот шаг, создаёт новый инстанс фото в БД."""

    def set_field(self, data):
        # to avoid awkward behavior while retrying the step multiple times
        self.model.photos.all().delete()
        if data["text"] == "Далее":
            return

        description = data["caption"]
        if not description:
            description = ""

        if data["photo"] and not data["callback"]:
            # todo сильно связано со структурой данных ТГ
            photo_file_id = data["photo"]
            photo = self.model.photos.create(
                # todo fix magic number, use textInput preprocessor?
                description=description[:250],
                tg_file_id=photo_file_id,
            )
            BOT_LOG.debug(
                LogStrings.DIALOG_SET_FIELD.format(
                    user_id=self.dialog.user.username,
                    stage=self.model.stage,
                    model=photo,
                    data=data,
                )
            )

        else:
            raise ImageNotProvidedError


class SetReadyInputProcessor(BaseInputProcessor):
    """Процессор подтверждения размещения в канале.

    Проверяет, что нажата кнопка подтверждения и запускает процесс перевода
    заявки в состояние готовности.
    Иначе обрабатывает исключительные ситуации (отказ от размещения или ввод
    данных вместо нажатия кнопки.
    """

    def __call__(self, dialog, data):
        if not data["callback"]:
            raise CallbackNotProvidedError
        elif data["callback"] == "restart":
            return
        elif data["callback"].split() == ["final_confirm", str(dialog.bound.pk)]:
            dialog.bound.set_ready(data["bot"])
            dialog.bound.stage_id += 1
            return
        raise ButtonIsLockedError


class FeedbackInputProcessor(TextInputProcessor):
    """Процессор ввода фидбека (сохраняется в регистрированной заявке)."""

    attr_name = "feedback"
    min_length = 3

    def get_step(self, data):
        return 1

    def set_field(self, data):
        self.model = self.dialog.bound.registered
        super().set_field(data)
        self.model.post_feedback(data["bot"])
