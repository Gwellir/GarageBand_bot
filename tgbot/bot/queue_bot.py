import telegram.bot
from telegram.ext import messagequeue as mq


class MQBot(telegram.bot.Bot):
    """Подкласс бота с имплементацией очереди сообщений"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)

        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except Exception:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super(MQBot, self).send_message(*args, **kwargs)
