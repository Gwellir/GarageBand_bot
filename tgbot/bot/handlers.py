from tgbot.bot.dialog import DialogProcessor
from tgbot.bot.senders import send_telegram_message
from tgbot.bot.utils import extract_user_data_from_update
from tgbot.models import Dialog


def message_handler(update, context):
    """Обработчик для всех получаемых сообщений.

    Передаёт информацию о событии соответствующему инстансу DialogProcessor"""

    # todo добавить привязку инстансов DialogProcessor к пользователям
    user_data = extract_user_data_from_update(update)
    dialog = Dialog.get_or_create(user_data)
    msg = update.effective_message
    input_data = {
        "bot": context.bot,
        "text": msg.text,
        "caption": msg.caption,
        "photo": msg.photo,
        "callback": update.callback_query,
    }
    dialog_processor = DialogProcessor(dialog, input_data)
    replies = dialog_processor.process()

    for reply in replies:
        send_telegram_message(reply, update.effective_user, context.bot)
