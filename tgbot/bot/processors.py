import abc

from logger.log_strings import LogStrings
from logger.log_config import BOT_LOG
from tgbot.models import RequestPhoto

from ..exceptions import NoCallbackProvidedError, NoTextProvidedError


class AbstractProcessor(metaclass=abc.ABCMeta):
    def __call__(self, dialog, data):
        pass


class DialogTextProcessor(AbstractProcessor):
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


class NameProcessor(DialogTextProcessor):
    attr_name = "name"

    def set_field(self, data):
        self.model = self.dialog.user
        super().set_field(data)


class TitleProcessor(DialogTextProcessor):
    attr_name = "title"


class DescriptionProcessor(DialogTextProcessor):
    attr_name = "description"


class LocationProcessor(DialogTextProcessor):
    attr_name = "location"


# todo add validation
class PhoneNumberProcessor(DialogTextProcessor):
    attr_name = "phone"


class StorePhotoProcessor(AbstractProcessor):
    def __call__(self, dialog, data):
        description = data["caption"]
        if not description:
            description = ""
        if data["photo"]:
            photo_file_id = data["photo"][-1].file_id
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


class SetReadyProcessor(AbstractProcessor):
    def __call__(self, dialog, data):
        if not data["callback"]:
            raise NoCallbackProvidedError
        dialog.request.set_ready(data["bot"])
