from tgbot.models import BotUser
from tgbot.bot.dialog import Dialog


def message_processor(update, context):
    user, created = BotUser.get_or_create(update, context)

    dialog = Dialog(user)
    dialog.process(update, context)
