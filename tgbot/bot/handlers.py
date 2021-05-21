import telegram

import tgbot.bot.strings as strings


def message_processor(update, context):
    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=strings.stage1_text,
        reply_markup=telegram.InlineKeyboardMarkup([
            [telegram.InlineKeyboardButton(text=strings.stage1_button1_text,
                                           callback_data='new_request')],
            [
                telegram.InlineKeyboardButton(text=strings.stage1_button2_text,
                                              callback_data='search_request'),
                telegram.InlineKeyboardButton(text=strings.stage1_button3_text,
                                              callback_data='propose_ads')
            ],
        ])
    )
