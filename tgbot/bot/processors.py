import abc

from tgbot.models import RequestPhoto

from ..exceptions import NoTextProvidedError


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
        if not data:
            raise NoTextProvidedError
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


class SetReadyProcessor(AbstractProcessor):
    def __call__(self, dialog, data):
        dialog.request.set_ready(data["bot"])
