import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

BOT_LOG = logging.getLogger("bot")

CONSOLE_LOGGER = logging.StreamHandler(sys.stderr)
FORMATTER = logging.Formatter("%(asctime)s %(levelname)-8s [bot] %(message)s")
CONSOLE_LOGGER.setFormatter(FORMATTER)
CONSOLE_LOGGER.setLevel(logging.DEBUG)
BOT_LOG.addHandler(CONSOLE_LOGGER)

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "bot.log")
FILE_LOGGER = TimedRotatingFileHandler(path, when="d", interval=1)
FILE_LOGGER.setFormatter(FORMATTER)
FILE_LOGGER.setLevel(logging.DEBUG)
BOT_LOG.addHandler(FILE_LOGGER)

BOT_LOG.setLevel(logging.DEBUG)
