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