from tgbot.bot import strings as strings


def fill_data(message_data, content_dict):
    msg = dict()
    msg["text"] = message_data["text"].format(**content_dict)
    msg["buttons"] = message_data["buttons"]
    for row in msg["buttons"]:
        for button in row:
            for field in button.keys():
                button[field] = button[field].format(**content_dict)

    return msg


def get_reply_for_stage(data, stage):
    num = stage - 1
    msg = fill_data(strings.stages_info[num], data)

    return msg


def get_admin_message(data: dict):
    msg = fill_data(strings.admin, data)

    return msg


def get_summary_for_request(data, photo, ready=False):
    msg = fill_data(strings.summary, data)
    msg["caption"] = msg.pop("text")
    msg["photo"] = photo
    if ready:
        msg.pop("buttons")

    return msg
