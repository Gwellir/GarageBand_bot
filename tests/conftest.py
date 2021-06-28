"""Конфигурационный файл pytest, содержит fixtures для работы функционального тест"""

import os

import dotenv
import pytest
from checks import BASE_DIR, IMAGE_PATH, STICKER_PATH
from telethon import TelegramClient
from telethon.sessions import StringSession

# load ENV
dotenv_file = BASE_DIR / ".env"
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

api_id = int(os.getenv("TG_TEST_API_ID"))
api_hash = os.getenv("TG_TEST_API_HASH")
session_str = os.getenv("TG_TEST_SESSION_STRING")


@pytest.fixture()
async def client() -> TelegramClient:
    """
    Инициализирует клиент telethon, выдаёт его инстанс в тест, затем закрывает клиент.
    """

    tc = TelegramClient(
        StringSession(session_str),
        api_id,
        api_hash,
        sequential_updates=True,
    )

    await tc.connect()
    await tc.get_me()
    await tc.get_dialogs()

    yield tc

    await tc.disconnect()
    await tc.disconnected


@pytest.fixture()
def image_path():
    """Выдаёт имя файла для тестового изображения."""

    return IMAGE_PATH


@pytest.fixture()
def sticker_path():
    """Выдаёт имя файла для тестового изображения."""

    return STICKER_PATH


@pytest.fixture()
def bot_name():
    """Выдаёт TG ID тестируемого бота."""

    return os.getenv("TESTED_BOT_ID")
