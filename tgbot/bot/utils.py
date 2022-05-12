"""Содержит набор утилит для обработчиков бота."""

import telegram
from django.utils.html import escape

from tgbot.exceptions import MessageIsAnEditError


def extract_user_data_from_update(update):
    """Извлекает данные о пользователе из формата update PTB."""

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
        raise MessageIsAnEditError(update)

    return dict(
        user_id=user["id"],
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name"]
            if k in user and user[k] is not None
        },
    )


def build_inline_button_markup(buttons_data):
    """Формирует reply_markup для сообщения с inline кнопками."""

    layout = []
    if buttons_data:
        for row in buttons_data:
            layout.append([telegram.InlineKeyboardButton(**item) for item in row])

        return telegram.InlineKeyboardMarkup(layout)

    return None


def build_reply_button_markup(buttons_data):
    """Формирует reply_markup для сообщения с текстовыми кнопками."""

    layout = []
    if buttons_data:
        for row in buttons_data:
            layout.append([telegram.KeyboardButton(**item) for item in row])

        return telegram.ReplyKeyboardMarkup(
            layout, one_time_keyboard=True, resize_keyboard=True
        )
    else:
        return telegram.ReplyKeyboardRemove()


# todo вынести в другое место, как относящееся к форматам логирования
def get_user_message_as_text(message_data: dict) -> str:
    """Возвращает сообщение пользователя в формате для просмотра чатов."""

    text = None
    if message_data["callback"]:
        text = f"CALLBACK: {message_data['callback']}"
    elif message_data["text"]:
        text = message_data["text"]
    elif message_data["caption"]:
        text = f"PHOTO: {message_data['photo']}\n\n{message_data['caption']}"

    return escape(text).replace("\n", "<br>")


def get_buttons_as_text(button_data):
    """Возвращает кнопки в текстовом виде."""

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
    """Возвращает сообщение бота в формате для сохранения в таблицу Message."""

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
