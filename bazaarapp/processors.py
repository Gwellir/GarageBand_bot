import re

from convoapp.processors import BaseInputProcessor, TextInputProcessor
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.exceptions import (
    ButtonIsLockedError,
    CallbackNotProvidedError,
    ImageNotProvidedError,
    IncorrectChoiceError,
    IncorrectNumberError,
    NotANumberError,
    TextNotProvidedError,
)


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


class IntNumberInputProcessor(BaseInputProcessor):
    min_value = 0
    max_value = 1000000000

    def get_int_value(self, text):
        try:
            result = int(float(text))
        except ValueError:
            raise NotANumberError
        if result < self.min_value or result > self.max_value:
            raise IncorrectNumberError
        return result

    def get_field_value(self, data):
        if not data["text"] or data["callback"]:
            raise TextNotProvidedError
        text = data.get("text")
        return self.get_int_value(text)

    def set_field(self, data):
        value = self.get_field_value(data)
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


class PriceInputProcessor(IntNumberInputProcessor):
    """Процессор ввода цены в долларах"""

    attr_name = "exact_price"

    def set_field(self, data):
        tag = self.model.get_tag_by_price(self.get_field_value(data))
        setattr(self.model, 'price_tag', tag)
        super().set_field(data)


class MileageInputProcessor(IntNumberInputProcessor):
    """Обработчик ввода километража."""

    attr_name = "mileage"
    max_value = 100000


class BinarySelectProcessor(BaseInputProcessor):
    """Обработчик ввода опций с бинарным выбором"""

    true_option_string = None
    false_option_string = None

    def get_binary_value(self, text):
        if text == self.true_option_string:
            return True
        elif text == self.false_option_string:
            return False
        else:
            raise IncorrectChoiceError(text)

    def get_field_value(self, data):
        if not data["text"] or data["callback"]:
            raise TextNotProvidedError
        text = data.get("text")
        return self.get_binary_value(text)

    def set_field(self, data):
        selection: bool = self.get_field_value(data)
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.dialog.user.username,
                stage=self.dialog.bound.stage,
                model=self.model,
                data=selection,
            )
        )
        setattr(self.model, self.attr_name, selection)
        self.model.save()


class BargainSelectProcessor(BinarySelectProcessor):
    """Описывает выбор возможности торга"""

    attr_name = "can_bargain"
    true_option_string = "Торг"
    false_option_string = "Без торга"


class AlbumPhotoProcessor(BaseInputProcessor):
    """Процессор ввода загруженной фотографии.

    Проверяет, не пропускается ли этот шаг, создаёт новый инстанс фото в БД."""

    album_dict = {}

    def cancel_step(self):
        self.model.photos.all().delete()

    def get_step(self, data):
        if data["text"] == "Отменить":
            self.cancel_step()
            if self.__class__.album_dict.get(self.dialog.user.user_id):
                self.__class__.album_dict.pop(self.dialog.user.user_id)
            return -1
        elif data["text"] == "Далее":
            self.dialog.suppress_output = False
            if self.__class__.album_dict.get(self.dialog.user.user_id):
                self.__class__.album_dict.pop(self.dialog.user.user_id)
            return 1
        else:
            if (
                data["media_group_id"]
                and self.__class__.album_dict.get(self.dialog.user.user_id)
                == data["media_group_id"]
            ):
                self.dialog.suppress_output = True
            else:
                self.dialog.suppress_output = False
            self.__class__.album_dict[self.dialog.user.user_id] = data["media_group_id"]
            return 0

    def set_field(self, data):
        # to avoid awkward behavior while retrying the step multiple times
        # self.model.photos.all().delete()
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


class LocationKeyInputProcessor(TextInputProcessor):
    """
    Процессор ввода района, где пользователь продаёт машину.
    """

    attr_name = "location_desc"


class LocationConfirmationProcessor(TextInputProcessor):
    """Процессор подтверждения выбора локации."""

    attr_name = "location_key"

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        city, region = re.findall(r'([\w\s.]+) \((\w\s.+)\)', data["text"])
        if not region:
            return
        return self.model._meta.get_field(self.attr_name).related_model.get(name=city)


class SetCompleteInputProcessor(BaseInputProcessor):
    """Процессор подтверждения завершения продажи.

    Проверяет, что нажата кнопка подтверждения и запускает процесс перевода
    объявления в завершённое состояние.
    Иначе обрабатывает исключительные ситуации (ввод
    данных вместо нажатия кнопки.
    """

    def __call__(self, dialog, data):
        if not data["callback"]:
            raise CallbackNotProvidedError
        elif data["callback"] == "restart":
            return
        elif data["callback"].split() == ["complete", str(dialog.bound.registered.pk)]:
            dialog.bound.set_sold()
            dialog.bound.stage_id += 1
            return
        raise ButtonIsLockedError
