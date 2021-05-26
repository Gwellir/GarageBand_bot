from tgbot.bot.dialog import DialogProcessor
from tgbot.models import BotUser


def message_processor(update, context):
    """Обработчик для всех получаемых сообщений.

    Передаёт информацию о событии соответствующему инстансу DialogProcessor"""

    # todo добавить привязку инстансов DialogProcessor к пользователям
    dialog = DialogProcessor(update)
    dialog.process(update, context)
