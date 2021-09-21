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
    LocationNotRecognizedError,
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

    def set_field(self, raw_text):
        super().set_field(raw_text)
        self.model.set_dict_data(
            tag_name=getattr(self.model, self.attr_name)
            .name.replace("$", "")
            .replace(" ", "_")
        )


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
        setattr(self.model, "price_tag", tag)
        super().set_field(data)
        self.model.set_dict_data(
            ad_price=getattr(self.model, self.attr_name),
            ad_price_range=getattr(self.model, "price_tag")
            .name.replace("$", "")
            .replace(" ", "_"),
        )


class MileageInputProcessor(IntNumberInputProcessor):
    """Обработчик ввода километража."""

    attr_name = "mileage"
    max_value = 100000

    def set_field(self, data):
        super().set_field(data)
        self.model.set_dict_data(ad_mileage=getattr(self.model, self.attr_name))


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

    def set_field(self, data):
        super().set_field(data)
        if getattr(self.model, self.attr_name):
            self.model.set_dict_data(ad_bargain_string="Торг!")


class AlbumPhotoProcessor(BaseInputProcessor):
    """Процессор ввода загруженной фотографии.

    Проверяет, не пропускается ли этот шаг, создаёт новый инстанс фото в БД."""

    album_dict = {}

    def cancel_step(self):
        self.model.photos.all().delete()
        self.model.set_dict_data(photos_loaded="")

    def get_step(self, data):
        album_dict = self.__class__.album_dict
        user_id = self.dialog.user.user_id
        if data["text"] == "Отменить":
            self.cancel_step()
            if album_dict.get(user_id):
                album_dict.pop(user_id)
            return -1
        elif data["text"] == "Далее":
            self.dialog.suppress_output = False
            if album_dict.get(user_id):
                album_dict.pop(user_id)
            return 1
        else:
            if (
                data["media_group_id"]
                and album_dict.get(user_id) == data["media_group_id"]
            ):
                self.dialog.suppress_output = True
            else:
                self.dialog.suppress_output = False
            album_dict[user_id] = data["media_group_id"]
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
            self.model.set_dict_data(photos_loaded="<pre>Фотографии загружены</pre>\n")

        else:
            raise ImageNotProvidedError


class LocationKeyInputProcessor(TextInputProcessor):
    """
    Процессор ввода района, где пользователь продаёт машину.
    """

    attr_name = "location_desc"

    def set_field(self, raw_text):
        super().set_field(raw_text)
        loc_name = raw_text.get("text")
        loc_model = self.model._meta.get_field("location_key").related_model
        locations = self.model.select_location_by_input(loc_name, loc_model)
        if not locations:
            raise LocationNotRecognizedError(loc_name)
        self.model.set_dict_data(
            ad_location=getattr(self.model, self.attr_name),
            location_selection=locations,
        )


class LocationConfirmationProcessor(TextInputProcessor):
    """Процессор подтверждения выбора локации."""

    attr_name = "location_key"

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        result = re.findall(r"([\w\s.\'-]+) \(регион: ([\w\s.-]+)\)", data["text"])
        if not result:
            raise IncorrectChoiceError(data["text"])
        else:
            city, region = result[0]
            rel_model = self.model._meta.get_field(self.attr_name).related_model
            return rel_model.objects.get(name=city, region__name=region)

    def set_field(self, raw_text):
        super().set_field(raw_text)
        self.model.set_dict_data(
            ad_region=getattr(self.model, self.attr_name)
            .region.name.replace(" ", "_")
            .replace("-", "_")
        )


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
        command = data["callback"].split()
        post_pk = dialog.bound.data_as_dict().get("registered_pk")
        if command == ["complete", str(post_pk)]:
            dialog.bound.set_sold()
            dialog.bound.stage_id += 1
            return
        elif command == ["renew", str(post_pk)]:
            dialog.bound.registered.repost()
            return
        raise ButtonIsLockedError
