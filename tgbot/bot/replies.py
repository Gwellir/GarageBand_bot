"""Содержит функции для формирования сообщений бота."""

import copy

from tgbot.bot import strings as strings


def fill_data(message_data: dict, content_dict: dict) -> dict:
    """Подставляет нужные данные в тело ответа и параметры кнопок."""

    msg = copy.deepcopy(message_data)
    msg["text"] = msg["text"].format(**content_dict)
    if msg.get("buttons") or msg.get("text_buttons"):
        for row in msg.get("buttons", []):
            for button in row:
                for field in button.keys():
                    button[field] = button[field].format(**content_dict)
        for row in msg.get("text_buttons", []):
            for button in row:
                for field in button.keys():
                    button[field] = button[field].format(**content_dict)

    return msg


def get_reply_for_stage(data, stage):
    """Возвращает шаблон сообщения, соответствующего переданной стадии диалога"""

    num = stage - 1
    msg = fill_data(strings.stages_info[num], data)

    return msg


def get_admin_message(data: dict):
    """Возвращает шаблон сообщения для администрирования."""

    msg = fill_data(strings.admin, data)

    return msg


def get_summary_for_request(data, photo, ready=False):
    """Возвращает шаблон саммари"""

    msg = fill_data(strings.summary, data)
    msg["caption"] = msg.pop("text")
    msg["photo"] = photo
    if ready:
        msg.pop("buttons")

    return msg
