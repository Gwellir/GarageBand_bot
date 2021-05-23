from django.db import IntegrityError
from telegram import ParseMode

from ..exceptions import BotProcessingError
from ..models import DialogStage
from .patterns import SingletonByUserID
from .stages import (
    CALLBACK_TO_STAGE,
    NEXT_STAGE,
    PROCESSORS,
    get_reply_for_stage,
    get_summary_for_request,
)


class Dialog(metaclass=SingletonByUserID):
    def __init__(self, user):
        self.user = user
        # todo implement reloading request drafts
        self.request = None
        self.bot = None
        self.stage = DialogStage.STAGE1_WELCOME

    def change_stage(self, update):
        callback = update.callback_query
        if callback is not None:
            self.stage = CALLBACK_TO_STAGE[callback.data]
        else:
            self.stage = NEXT_STAGE.get(self.stage, self.stage)
        self.user.dialog_stage = self.stage
        self.user.save()

    def operate_data(self, context, update):
        if self.stage in PROCESSORS.keys():
            self.user, self.request = PROCESSORS[self.stage](
                context, update, self.user, self.request
            )

    def process(self, update, context):
        self.bot = context.bot
        try:
            self.operate_data(context, update)
            self.change_stage(update)
        except (IntegrityError, BotProcessingError) as e:
            print(e.args)
            self.send_got_wrong_data()
        self.send_reply(get_reply_for_stage(self.stage))
        if self.stage == DialogStage.STAGE10_CHECK_DATA:
            self.show_summary(get_summary_for_request(self.request))

    def send_got_wrong_data(self):
        self.bot.send_message(
            chat_id=self.user.user_id,
            text="Отправлены неверные данные, попробуйте ещё раз!",
        )

    def send_reply(self, reply, params=None):
        self.bot.send_message(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN_V2, **reply
        )

    def show_summary(self, summary):
        self.bot.send_photo(
            chat_id=self.user.user_id, parse_mode=ParseMode.MARKDOWN, **summary
        )
