import abc
import re

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.models import RequestPhoto

from ..exceptions import (
    CallbackNotProvidedError,
    ImageNotProvidedError,
    PhoneNumberMalformedError,
    TextNotProvidedError,
)


class AbstractInputProcessor(metaclass=abc.ABCMeta):
    def __call__(self, dialog, data):
        pass


class TextInputProcessor(AbstractInputProcessor):
    attr_name = None

    def __call__(self, dialog, data):
        self.dialog = dialog
        self.model = dialog.request
        self.set_field(self.get_cleaned_text(data))

    def get_cleaned_text(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        return data.get("text")

    def set_field(self, text):
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.dialog.user.username,
                stage=self.dialog.dialog.stage,
                model=self.model,
                data=text,
            )
        )
        setattr(self.model, self.attr_name, text)
        self.model.save()


class NameInputProcessor(TextInputProcessor):
    attr_name = "name"

    def set_field(self, data):
        self.model = self.dialog.user
        super().set_field(data)


class TitleInputProcessor(TextInputProcessor):
    attr_name = "title"


class DescriptionInputProcessor(TextInputProcessor):
    attr_name = "description"


class LocationInputProcessor(TextInputProcessor):
    attr_name = "location"


# todo move validation to the model
class PhoneNumberInputProcessor(TextInputProcessor):
    attr_name = "phone"

    def get_cleaned_text(self, data):
        text = super().get_cleaned_text(data)
        cleaned_text = re.sub(r"[^+0-9]", "", text)
        if not (7 < len(cleaned_text) < 15) or cleaned_text.find("+", 1) >= 0:
            raise PhoneNumberMalformedError
        return cleaned_text


class StorePhotoInputProcessor(AbstractInputProcessor):
    def __call__(self, dialog, data):
        description = data["caption"]
        if not description:
            description = ""
        if data["photo"]:
            photo_file_id = data["photo"]
            photo = RequestPhoto(
                description=description,
                request=dialog.request,
                tg_file_id=photo_file_id,
            )
            photo.save()
        # todo странный flow-control
        elif not data["callback"]:
            raise ImageNotProvidedError
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=dialog.user.username,
                stage=dialog.dialog.stage,
                model="RequestPhoto",
                data=data,
            )
        )


class SetReadyInputProcessor(AbstractInputProcessor):
    def __call__(self, dialog, data):
        if not data["callback"]:
            raise CallbackNotProvidedError
        dialog.request.set_ready(data["bot"])
