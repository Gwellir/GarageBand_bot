from convoapp.processors import BaseInputProcessor, TextInputProcessor
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.exceptions import (
    ImageNotProvidedError,
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


class AlbumPhotoProcessor(BaseInputProcessor):
    """Процессор ввода загруженной фотографии.

    Проверяет, не пропускается ли этот шаг, создаёт новый инстанс фото в БД."""

    def cancel_step(self):
        self.model.photos.all().delete()

    def get_step(self, data):
        if data["text"] == "Отменить":
            self.cancel_step()
            return -1
        elif data["text"] == "Далее":
            self.dialog.suppress_output = False
            return 1
        else:
            self.dialog.suppress_output = True
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
