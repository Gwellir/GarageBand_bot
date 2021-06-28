from telethon.tl.custom import Message


async def text_reply(conv, text, **kwargs):
    await conv.send_message(text, **kwargs)
    answer: Message = await conv.get_response()
    return answer


async def click_button(conv, message, button_text):
    await message.click(text=button_text)
    answer: Message = await conv.get_response()
    return answer
