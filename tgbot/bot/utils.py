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

        return telegram.ReplyKeyboardMarkup(layout, one_time_keyboard=True)

    return None
