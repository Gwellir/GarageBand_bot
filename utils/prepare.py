#!/bin/python3
"""
Скрипт для автоматизации развёртывания Python проектов на базе Django,
настройки виртуального окружения для них и выполнения базовых миграций.

При запуске в директории с дистрибутивом - создаёт виртуальное окружение Python,
устанавливает туда пакеты в соответствии с требованиями проекта
и инициирует базу данных.
"""


import os
import platform
import shutil
import subprocess
import sys

VENV_DIR_NAME = "venv"
REQ_FILE = "requirements.txt"
PYTHON = sys.executable
if platform.system() == "Windows":
    PIP_ENV = f"{VENV_DIR_NAME}/Scripts/pip3.exe"
    PYTHON_ENV = f"{VENV_DIR_NAME}/Scripts/python.exe"
elif platform.system() in ["Linux", "Darwin"]:
    PYTHON_ENV = f"{VENV_DIR_NAME}/bin/python3"
    PIP_ENV = f"{VENV_DIR_NAME}/bin/pip3"
else:
    print("Unknown OS!\nExiting")
    sys.exit(1)


def setup_env() -> None:
    # delete existing venv
    if os.path.isdir(VENV_DIR_NAME):
        print("Cleaning existing venv...")
        shutil.rmtree(VENV_DIR_NAME)
    # create new virtualenv
    subprocess.run([PYTHON, "-m", "venv", VENV_DIR_NAME], check=True)
    run_preparations()


def run_preparations() -> None:
    # upgrade env pip just in case
    subprocess.run([PYTHON_ENV, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    # install project requirements
    subprocess.run([PIP_ENV, "install", "-r", REQ_FILE], check=True)
    # perform migrations
    # subprocess.run([PYTHON_ENV, "manage.py", "makemigrations"], check=True)
    subprocess.run([PYTHON_ENV, "manage.py", "migrate"], check=True)


if __name__ == "__main__":
    # check python version
    if sys.version_info >= (3, 6, 1):
        print("Python version check - OK")
    else:
        print(
            "You need to upgrade your Python interpreter to version 3.6.1 at least!\n"
            "Exiting..."
        )
        sys.exit(1)

    setup_env()
