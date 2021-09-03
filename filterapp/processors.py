from convoapp.processors import BaseInputProcessor
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.exceptions import TextNotProvidedError


class MultiSelectProcessor(BaseInputProcessor):
    """Обработчик ввода множественных опций"""

    def get_step(self, data):
        if data["text"] == "Отменить":
            return -1
        elif data["text"] == "Далее":
            return 1
        else:
            return 0

    def get_field_value(self, data):
        if not data["text"]:
            raise TextNotProvidedError
        text = data["text"][2:]
        rel_model = self.model._meta.get_field(self.attr_name).related_model
        return rel_model.get_tag_by_text(text)

    def set_field(self, data):
        if data["text"] == "Далее":
            return

        value = self.get_field_value(data)
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.dialog.user.username,
                stage=self.dialog.bound.stage,
                model=self.model,
                data=value,
            )
        )
        field = getattr(self.model, self.attr_name)
        if value not in field.all():
            field.add(value)
        else:
            field.remove(value)
        self.model.save()


class PriceMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "price_ranges"


class RegionMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "regions"