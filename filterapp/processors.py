from telegram.error import BadRequest

from bazaarapp.processors import IntNumberInputProcessor
from convoapp.processors import BaseInputProcessor, TextInputProcessor
from filterapp.exceptions import NotSubscribedError
from logger.log_config import BOT_LOG
from logger.log_strings import LogStrings
from tgbot.bot.utils import build_inline_button_markup
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
        self.model.set_dict_data(
            filter_pk=self.model.pk,
        )

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
        service = self.state_machine.bound.get_service_name()
        if not self.state_machine.user.subscribed_to_service(service):
            raise NotSubscribedError

    def _get_checkout_link(self):
        checkout = self.model.make_subscription()
        self.model.set_dict_data(
            checkout_url=checkout.link,
        )
        sm = self.state_machine
        del sm.users_cache[
            (
                sm.message_data.get("bot"),
                sm.user.user_id,
            )
        ]

    def _check_free_sub(self):
        return self.model.has_never_subbed()

    def _make_free_sub(self):
        self.model.make_subscription(free=True)

    def get_step(self, data):
        if data["text"] == "Отменить":
            self.cancel_step()
            return -1
        elif data["text"] == "Оплатить":
            self._get_checkout_link()
            return 1
        else:
            if self._check_free_sub():
                self._make_free_sub()
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
            # hacks upon hacks
            # self._switch_keyboard_value(data, value.name)
        else:
            field.remove(value)
            # self._switch_keyboard_value(data, value.name, disable=True)
        self._update_keyboard(data["query"].message)

        self.state_machine.suppress_output = True
        self.model.save()
        self.model.set_dict_data(
            **{self.attr_name: ", ".join([r.name for r in field.all()])}
        )

    def _update_keyboard(self, message):
        msg_data: dict = self.model.get_reply_for_stage()
        message.edit_reply_markup(
            reply_markup=build_inline_button_markup(msg_data["buttons"])
        )

    def _switch_keyboard_value(self, data: dict, name, disable=False):
        mark = "☐" if disable else "☑"
        msg = data["query"].message
        keyboard = msg.reply_markup.inline_keyboard
        for row in keyboard:
            for button in row:
                if button.text[2:] == name:
                    button.text = f"{mark} {name}"
                    break
        try:
            msg.edit_reply_markup(reply_markup=msg.reply_markup)
        except BadRequest:
            BOT_LOG.warn(
                LogStrings.DIALOG_SAME_MESSAGE.format(
                    user_id=self.state_machine.user.username,
                    stage=self.model.stage,
                    model=self.model,
                )
            )


class LowPriceInputProcessor(IntNumberInputProcessor):
    attr_name = "low_price"

    def set_field(self, data):
        if data["text"] == "Пропустить":
            data["text"] = self.min_value

        super().set_field(data)
        self.state_machine.bound.set_dict_data(
            **{self.attr_name: getattr(self.model, self.attr_name)},
        )


class HighPriceInputProcessor(IntNumberInputProcessor):
    attr_name = "high_price"

    def set_field(self, data):
        if data["text"] == "Пропустить":
            data["text"] = self.max_value

        super().set_field(data)
        self.state_machine.bound.set_dict_data(
            **{self.attr_name: getattr(self.model, self.attr_name)},
        )


class RegionMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "regions"


class RepairsMultiSelectProcessor(MultiSelectProcessor):
    attr_name = "repair_types"


class CompanyNameInputProcessor(TextInputProcessor):
    """Процессор ввода имени компании (сохраняет имя в модели пользователя)."""

    attr_name = "company_name"
    min_length = 3

    def set_field(self, data):
        self.model = self.state_machine.user
        super().set_field(data)
        self.state_machine.bound.set_dict_data(
            company_name=getattr(self.model, self.attr_name),
        )
