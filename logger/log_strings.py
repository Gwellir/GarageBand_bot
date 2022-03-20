# todo load this from .ini
class LogStrings:
    """Класс для работы с текстовыми строками логгера."""

    USER_DATA_FROM_UPDATE = "[TG user data] >>> {user_data}"
    DIALOG_INCOMING_MESSAGE = (
        "<-- : User: {user_id}, stage: {stage}, data: {input_data}"
    )
    DIALOG_INPUT_ERROR = "WRONG: User: {user_id}, stage: {stage}, args: {args}"
    DIALOG_REQUEST_ERROR = "NO REQUEST: User: {user_id}, stage: {stage}, args: {args}"
    DIALOG_RESTART = "RESTART: User: {user_id}, stage: {stage}"
    DIALOG_SEND_MESSAGE = "--> : User: {user_id}, reply: {reply}"
    DIALOG_PUBLISH_REQUEST = (
        "PUBLISH : User: {user_id}, channel: {channel_id}, summary: {summary}"
    )
    DIALOG_CHANGE_STAGE = (
        "STAGE: User: {user_id}, stage: {stage} -> {new_stage}, callback: {callback}"
    )
    DIALOG_SET_FIELD = (
        "FIELD: User: {user_id}, stage: {stage}, model: {model}, data: {data}"
    )
    DIALOG_SET_READY = (
        "READY: User: {user_id}, request: {request_id}, saved {photos_count} photos"
    )
    DIALOG_SET_SOLD = "SOLD: User: {user_id}, ad: {request_id}"

    DIALOG_SAME_MESSAGE = (
        "SAME KEYBOARD: user: {user_id}, model: {model}, stage: {stage}"
    )

    CHANNEL_POST = "POST: channel: {channel_id}"
