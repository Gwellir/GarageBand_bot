import re

from django.utils.html import strip_tags

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings

from ..exceptions import (
    CallbackNotProvidedError,
    ImageNotProvidedError,
    PhoneNumberMalformedError,
    TextNotProvidedError,
    TextTooLongError,
    TextTooShortError,
)
from ..models import Tag


class BaseInputProcessor:
    attr_name = None

    def __call__(self, dialog, data):
        self.dialog = dialog
        self.model = dialog.request
        step = self.get_step(data)
        if step > 0:
            self.set_field(data)

        return step

    def set_field(self, data):
        pass

    def get_step(self, data):
        if data["text"] == "Отменить":
            return -1
        else:
            return 1


class StartInputProcessor(BaseInputProcessor):
    def get_step(self, data):
        if data["text"] == "Оформить заявку":
            return 1
        return 0


class TextInputProcessor(BaseInputProcessor):
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
                stage=self.dialog.dialog.stage,
                model=self.model,
                data=value,
            )
        )
        setattr(self.model, self.attr_name, value)
        self.model.save()


class NameInputProcessor(TextInputProcessor):
    attr_name = "name"
    min_length = 2

    def set_field(self, data):
        self.model = self.dialog.user
        super().set_field(data)


class TagInputProcessor(TextInputProcessor):
    attr_name = "tag"

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        text = data["text"]
        try:
            tag = Tag.objects.get(name=text.replace(" ", "_").replace("/", "_"))
        except Tag.DoesNotExist:
            tag = Tag.objects.get(pk=1)  # default "Другое"

        return tag


class DescriptionInputProcessor(TextInputProcessor):
    attr_name = "description"


class LocationInputProcessor(TextInputProcessor):
    attr_name = "location"


# todo move validation to the model
class PhoneNumberInputProcessor(TextInputProcessor):
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
    def set_field(self, data):
        # to avoid awkward behavior while retrying the step multiple times
        self.model.photos.all().delete()
        if data["text"] == "Пропустить":
            return

        description = data["caption"]
        if not description:
            description = ""

        if data["photo"] and not data["callback"]:
            photo_file_id = data["photo"]
            self.model.photos.create(
                # todo fix magic number, use textInput preprocessor?
                description=description[:250],
                tg_file_id=photo_file_id,
            )
            BOT_LOG.debug(
                LogStrings.DIALOG_SET_FIELD.format(
                    user_id=self.dialog.user.username,
                    stage=self.dialog.dialog.stage,
                    model="RequestPhoto",
                    data=data,
                )
            )

        else:
            raise ImageNotProvidedError


class SetReadyInputProcessor(BaseInputProcessor):
    def __call__(self, dialog, data):
        if not data["callback"]:
            raise CallbackNotProvidedError
        if data["callback"] == "restart":
            return 0
        dialog.request.set_ready(data["bot"])
        return 1
