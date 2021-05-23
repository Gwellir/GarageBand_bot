from tgbot.bot.dialog import Dialog
from tgbot.models import BotUser


def message_processor(update, context):
    user, created = BotUser.get_or_create(update, context)

    dialog = Dialog(user)
    dialog.process(update, context)
