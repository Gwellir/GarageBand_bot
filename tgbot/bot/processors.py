import abc

from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.models import RequestPhoto

from ..exceptions import NoCallbackProvidedError, NoTextProvidedError, NoImageProvidedError


class AbstractInputProcessor(metaclass=abc.ABCMeta):
    def __call__(self, dialog, data):
        pass


class TextInputProcessor(AbstractInputProcessor):
    attr_name = None

    def __call__(self, dialog, data):
        self.dialog = dialog
        self.model = dialog.request
        self.set_field(data)

    def set_field(self, data):
        if not data["text"]:
            raise NoTextProvidedError
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.dialog.user.username,
                stage=self.dialog.dialog.stage,
                model=self.model,
                data=data["text"],
            )
        )
        setattr(self.model, self.attr_name, data["text"])
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


# todo add validation
class PhoneNumberInputProcessor(TextInputProcessor):
    attr_name = "phone"


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


class SetReadyInputProcessor(AbstractInputProcessor):
    def __call__(self, dialog, data):
        if not data["callback"]:
            raise NoCallbackProvidedError
        dialog.request.set_ready(data["bot"])
