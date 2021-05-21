from .strings import stage1_text


def message_processor(update, context):
    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=stage1_text,
    )
