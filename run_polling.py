import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "garage_band_bot.settings")
django.setup()

from tgbot.bot.dispatcher import run_polling  # noqa: E402

if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    run_polling()
