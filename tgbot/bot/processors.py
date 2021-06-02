import abc
import re

from django.utils.html import strip_tags

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.models import RequestPhoto

from ..exceptions import (
    CallbackNotProvidedError,
    ImageNotProvidedError,
    PhoneNumberMalformedError,
    TextNotProvidedError,
    TextTooLongError,
    TextTooShortError,
)


class AbstractInputProcessor(metaclass=abc.ABCMeta):
    def __call__(self, dialog, data):
        pass


class TextInputProcessor(AbstractInputProcessor):
    attr_name = None
    min_length = 3

    def __call__(self, dialog, data):
        self.dialog = dialog
        self.model = dialog.request
        self.set_field(data)

    def check_text_length(self, text):
        text_length = len(text)
        max_length = self.model._meta.get_field(self.attr_name).max_length
        if text_length < self.min_length:
            raise TextTooShortError(self.min_length, text_length)
        elif text_length > max_length:
            raise TextTooLongError(max_length, text_length)
        else:
            return True

    def get_cleaned_text(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        text = data.get("text")
        if self.check_text_length(text):
            return strip_tags(text)

    def set_field(self, raw_text):
        text = self.get_cleaned_text(raw_text)
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
    min_length = 2

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
            BOT_LOG.debug(
                LogStrings.DIALOG_SET_FIELD.format(
                    user_id=dialog.user.username,
                    stage=dialog.dialog.stage,
                    model="RequestPhoto",
                    data=data,
                )
            )
        # todo странный flow-control
        elif not data["callback"]:
            raise ImageNotProvidedError


class SetReadyInputProcessor(AbstractInputProcessor):
    def __call__(self, dialog, data):
        if not data["callback"]:
            raise CallbackNotProvidedError
        dialog.request.set_ready(data["bot"])
