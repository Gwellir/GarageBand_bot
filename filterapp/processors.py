from bazaarapp.processors import IntNumberInputProcessor
from convoapp.processors import BaseInputProcessor
from filterapp.exceptions import NotSubscribedError
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from subscribeapp.constants import ServiceChoice
from tgbot.exceptions import (
    IncorrectChoiceError,
    TextNotProvidedError,
    UserNotInChannelError,
)


class SubCheckProcessor(BaseInputProcessor):
    def _check_follow(self):
        instance = self.model.get_tg_instance()
        bot = instance.tg_bot
        channel_id = instance.publish_id
        user_id = self.state_machine.user.user_id
        member = bot.get_chat_member(channel_id, user_id)
        if member.status in ["left", "kicked"]:
            raise UserNotInChannelError(instance.publish_name)

    def get_step(self, data):
        if data["text"] == "Отменить":
            self.cancel_step()
            return -1
        elif data["text"] == "Далее":
            self._check_follow()
            return 1
        else:
            return 0


class ConfirmPaymentProcessor(BaseInputProcessor):
    def _check_sub(self):
        # todo make filterapp aware of which bot it works with
        if not self.state_machine.user.subscribed_to_service(ServiceChoice.REPAIRS_BOT):
            raise NotSubscribedError

    def _get_checkout_link(self):
        checkout = self.model.make_subscription()
        self.model.set_dict_data(
            checkout_url=checkout.link,
        )
        del self.state_machine.users_cache[
            (
                self.state_machine.message_data.get("bot"),
                self.state_machine.user.user_id,
            )
        ]

    def get_step(self, data):
        if data["text"] == "Отменить":
            self.cancel_step()
            return -1
        elif data["text"] == "Оплатить":
            self._get_checkout_link()
            return 1
        else:
            self._check_sub()
            return 2


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
        try:
            value = rel_model.get_tag_by_name(text)
        except rel_model.DoesNotExist:
            raise IncorrectChoiceError(data["text"])
        return value

    def set_field(self, data):
        field = getattr(self.model, self.attr_name)
        if data["text"] == "Далее":
            if not field.all():
                rel_model = self.model._meta.get_field(self.attr_name).related_model
                field.add(*rel_model.objects.all())
            return

        value = self.get_field_value(data)
        BOT_LOG.debug(
            LogStrings.DIALOG_SET_FIELD.format(
                user_id=self.state_machine.user.username,
                stage=self.state_machine.bound.stage,
                model=self.model,
                data=value,
            )
        )
        if value not in field.all():
            field.add(value)
        else:
            field.remove(value)
        self.model.save()


class LowPriceInputProcessor(IntNumberInputProcessor):
    attr_name = "low_price"

    def set_field(self, data):
        if data["text"] == "Пропустить":
            data["text"] = self.min_value

        super().set_field(data)


class HighPriceInputProcessor(IntNumberInputProcessor):
    attr_name = "high_price"

    def set_field(self, data):
        if data["text"] == "Пропустить":
            data["text"] = self.max_value

        super().set_field(data)


class RegionMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "regions"


class RepairsMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "repair_types"
