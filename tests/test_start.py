import os

from pytest import mark
from telethon import TelegramClient
from telethon.tl.custom.message import Message

BOT_ID = os.getenv("tested_bot_id")


@mark.asyncio
async def test_start(client: TelegramClient):
    async with client.conversation("@GarageBandTest_bot", timeout=5) as conv:
        await conv.send_message("/start")

        resp: Message = await conv.get_response()

        assert "приёма заявок Garage Band" in resp.raw_text
        assert resp.button_count == 3
        assert resp.buttons[0][0].text == "Создать новую заявку"
        assert resp.buttons[1][0].text == "Поиск заявок"
        assert resp.buttons[1][1].text == "Разместить рекламу"

        await resp.click(text="Создать новую заявку")
        answer = await conv.get_response()
        assert answer.button_count == 2
        assert "создать новую заявку" in answer.raw_text
        assert answer.buttons[0][0].text == "Начать оформление"
        assert answer.buttons[1][0].text == "Отменить"

        await answer.click(text="Начать оформление")
        answer = await conv.get_response()
        assert answer.button_count == 1
        assert "Представьтесь, пожалуйста" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("Владислав Юрь")
        answer = await conv.get_response()

        assert answer.button_count == 1
        assert "название заявки" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"
