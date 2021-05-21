import dotenv
import os

from pathlib import Path
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

BASE_DIR = Path(__file__).resolve().parent.parent

# load ENV
dotenv_file = BASE_DIR / ".env"
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

api_id = os.getenv("TG_TEST_API_ID")
api_hash = os.getenv("TG_TEST_API_HASH")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Your session string is:", client.session.save())
