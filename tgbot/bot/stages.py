import telegram

import tgbot.bot.strings as strings
from tgbot.models import DialogStage


def build_button_markup(buttons_data):
    layout = []
    for row in buttons_data:
        layout.append([telegram.InlineKeyboardButton(**item) for item in row])

    return telegram.InlineKeyboardMarkup(layout)


def get_reply_for_stage(stage):
    num = stage.value - 1
    text = strings.stages_info[num]['text']
    markup = build_button_markup(strings.stages_info[num]['buttons'])

    return dict(text=text, reply_markup=markup)


def store_name(update, user, request):
    user.name = update.effective_message.text
    user.save()


PROCESSORS = {
    DialogStage.STAGE3_GET_NAME: store_name,
}


CALLBACK_TO_STAGE = {
    "new_request": DialogStage.STAGE2_CONFIRM_START,
    "restart": DialogStage.STAGE1_WELCOME,
    "stage2_confirm": DialogStage.STAGE3_GET_NAME,
}

NEXT_STAGE = {
    DialogStage.STAGE1_WELCOME: DialogStage.STAGE1_WELCOME,
    DialogStage.STAGE3_GET_NAME: DialogStage.STAGE4_GET_REQUEST_NAME,
}
