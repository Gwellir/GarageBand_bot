from .stages import (get_reply_for_stage, get_summary_for_request, NEXT_STAGE, CALLBACK_TO_STAGE, PROCESSORS)
from ..models import DialogStage


class SingletonByUserID(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            user_id = args[0].id
        else:
            return

        if user_id in cls.__instance:
            return cls.__instance[user_id]
        else:
            cls.__instance[user_id] = super().__call__(*args, **kwargs)
            return cls.__instance[user_id]


class Dialog(metaclass=SingletonByUserID):

    def __init__(self, user):
        self.user = user
        self.request = None
        self.bot = None
        self.stage = user.dialog_stage

    def change_stage(self, update):
        callback = update.callback_query
        if callback is not None:
            self.stage = CALLBACK_TO_STAGE[callback.data]
        else:
            self.stage = NEXT_STAGE[self.stage]
        self.user.dialog_stage = self.stage
        self.user.save()

    def operate_data(self, context, update):
        if self.stage in PROCESSORS.keys():
            self.user, self.request = PROCESSORS[self.stage](context, update, self.user, self.request)

    def process(self, update, context):
        self.bot = context.bot
        self.operate_data(context, update)
        self.change_stage(update)
        self.send_reply(get_reply_for_stage(self.stage))
        if self.stage == DialogStage.STAGE10_CHECK_DATA:
            self.show_summary(get_summary_for_request(self.request))

    def send_reply(self, reply, params=None):
        self.bot.send_message(chat_id=self.user.user_id, **reply)

    def show_summary(self, summary):
        self.bot.send_photo(chat_id=self.user.user_id, **summary)
