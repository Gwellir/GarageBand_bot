import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garage_band_bot.settings')
django.setup()

from tgbot.bot.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()
