import os
from pathlib import Path

import dotenv
import pytest
from telethon import TelegramClient
from telethon.sessions import StringSession

BASE_DIR = Path(__file__).resolve().parent.parent

# load ENV
dotenv_file = BASE_DIR / ".env"
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

api_id = int(os.getenv("TG_TEST_API_ID"))
api_hash = os.getenv("TG_TEST_API_HASH")
session_str = os.getenv("TG_TEST_SESSION_STRING")


@pytest.fixture()
async def client() -> TelegramClient:
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
def image():
    return BASE_DIR / "tests/clouds-mf.jpg"


@pytest.fixture()
def bot_name():
    return os.getenv("TESTED_BOT_ID")
