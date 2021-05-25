from tgbot.bot.dialog import DialogProcessor
from tgbot.models import BotUser


def message_processor(update, context):

    dialog = DialogProcessor(update)
    dialog.process(update, context)
