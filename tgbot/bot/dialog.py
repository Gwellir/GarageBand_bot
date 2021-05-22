from .stages import get_reply_for_stage, NEXT_STAGE, CALLBACK_TO_STAGE, PROCESSORS


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

    def operate_input(self, update):
        if self.stage in PROCESSORS.keys():
            PROCESSORS[self.stage](update, self.user, self.request)

    def process(self, update, context):
        self.bot = context.bot
        self.operate_input(update)
        self.change_stage(update)
        self.send_reply(get_reply_for_stage(self.stage))

    def send_reply(self, reply, params=None):
        self.bot.send_message(chat_id=self.user.user_id, **reply)
