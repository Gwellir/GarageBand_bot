import telegram


def extract_user_data_from_update(update):
    """python-telegram-bot's Update instance --> User info"""
    if update.message is not None:
        user = update.message.from_user.to_dict()
    elif update.inline_query is not None:
        user = update.inline_query.from_user.to_dict()
    elif update.chosen_inline_result is not None:
        user = update.chosen_inline_result.from_user.to_dict()
    elif (
        update.callback_query is not None
        and update.callback_query.from_user is not None
    ):
        user = update.callback_query.from_user.to_dict()
    elif (
        update.callback_query is not None and update.callback_query.message is not None
    ):
        user = update.callback_query.message.chat.to_dict()
    else:
        raise Exception(f"Can't extract user data from update: {update}")

    return dict(
        user_id=user["id"],
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name"]
            if k in user and user[k] is not None
        },
    )


def build_inline_button_markup(buttons_data):
    layout = []
    if buttons_data:
        for row in buttons_data:
            layout.append([telegram.InlineKeyboardButton(**item) for item in row])

        return telegram.InlineKeyboardMarkup(layout)

    return None


def build_reply_button_markup(buttons_data):
    layout = []
    if buttons_data:
        for row in buttons_data:
            layout.append([telegram.KeyboardButton(**item) for item in row])

        return telegram.ReplyKeyboardMarkup(
            layout, one_time_keyboard=True, resize_keyboard=True
        )
    else:
        return telegram.ReplyKeyboardRemove()


def get_user_message_as_text(message_data: dict) -> str:
    text = None
    if message_data["callback"]:
        text = f"CALLBACK: {message_data['callback']}"
    elif message_data["text"]:
        text = message_data["text"]
    elif message_data["caption"]:
        text = f"PHOTO: {message_data['photo']}<br><br>{message_data['caption']}"

    return text.replace("\n", "<br>")


def get_buttons_as_text(button_data):
    text = ""
    if not button_data:
        return text
    for row in button_data:
        text = f"{text}<br>"
        for button in row:
            if "callback_data" in button.keys():
                command_text = f"({button['callback_data']})"
            elif "url" in button.keys():
                command_text = f"({button['url']})"
            else:
                command_text = ""
            text = f"{text}[{button['text']}{command_text}] "

    return text


def get_bot_message_as_text(message_data: dict) -> str:
    if "text" in message_data.keys():
        text = message_data["text"]
    elif "caption" in message_data.keys():
        text = f"PHOTO: {message_data['photo']}<br><br>{message_data['caption']}"
    text = text.replace("\n", "<br>")
    button_text = ""
    if "buttons" in message_data.keys():
        button_text = get_buttons_as_text(message_data["buttons"])
    elif "text_buttons" in message_data.keys():
        button_text = get_buttons_as_text(message_data["text_buttons"])
    text = f"{text}{button_text}"
    return text
