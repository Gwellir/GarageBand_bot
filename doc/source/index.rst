.. Garage Band bot documentation master file, created by
   sphinx-quickstart on Tue Jun 22 14:37:15 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Документация для Telegram бота Garage Band
===========================================

Garage Band bot позволяет принимать и регистрировать заявки на авторемонт и
обслуживание по установленной форме, для размещения их в канале, который
просматривается владельцами частных автомастерских.

В боте реализована валидация вводимых данных с подсказками пользователю, сохранение
текущих этапов оформления заявок, а также базовые функции администрирования и просмотра
логов бесед с пользователями.


Порядок развёртывания
~~~~~~~~~~~~~~~~~~~~~

**Пример для Ubuntu 20.***

Для работы с настройками по умолчанию потребуется установить postgresql и создать там
пустую базу garageband

.. note::
   Для работы с другой базой данных - нужно изменить URL базы данных в
   **DATABASE_URL** и установить/подключить соответствующее иное решение.

Для работы с ботом и веб-частью используется пользователь django в группе www-data.

После скачивания кода из репозитория и установки python и pip - запустить в корневой
директории проекта ``python3 utils/prepare.py`` - команда создаст виртуальное окружение,
установит требуемые пакеты и выполнит миграции базы данных.
Для создания суперпользователя для админки Django следует (в виртуальном окружении)
выполнить команду ``python3 manage.py createsuperuser``.

Требуемые переменные окружения:
"""""""""""""""""""""""""""""""

``DJANGO_SECRET_KEY=<КЛЮЧ>`` - задаёт секретный ключ для работы Django, требования в
документации.

``DJANGO_DEBUG=0`` - выключает дебаг режим в Django, подключает основной набор каналов
и групп для работы

``PUBLISHING_CHANNEL_ID=<ID>`` - задаёт telegram id основного канала для публикаций заявок

``PUBLISHING_CHANNEL_NAME=<НАЗВАНИЕ>`` - указывает название этого канала (без @), для
подстановок

``ADMIN_GROUP_ID=<ID>`` - задаёт telegram id группы для управления, куда выводятся
админские оповещения

``DISCUSSION_GROUP_ID=<ID>`` - группа обсуждений, подключённая к каналу
(указана для модерации)

``TELEGRAM_TOKEN=<ТОКЕН>`` - токен бота, полученный от BotFather

``DATABASE_URL=<URL>`` - ссылка на базу данных,
пример: postgresql://postgres:postgres@localhost/garageband

``DEV_TG_ID=<ID>`` - telegram id разработчика, туда будут приходить оповещения обо всех
необработанных исключениях в работе

Настройка автозапуска telegram бота
"""""""""""""""""""""""""""""""""""

Подключение решения в виде сервиса:
::

   # /etc/systemd/system/garagebandbot.service
   [Unit]
   Description = Telegram bot service for Garage Band project
   After = network.target

   [Service]
   Type = simple
   ExecStart = /home/django/GarageBand_bot/venv/bin/python3 /home/django/GarageBand_bot/run_polling.py
   User = django
   Group = www-data
   Restart = on-failure
   SyslogIdentifier = garagebandbot
   RestartSec = 5
   TimeoutStartSec = infinity

   [Install]
   WantedBy = multi-user.target

После выполнения ``sudo systemctl daemon-reload``, запуск сервиса будет доступен
по команде ``sudo systemctl start garagebandbot``.

Настройка веб-интерфейса
""""""""""""""""""""""""

Для работы с веб-интерфейсом в деплое данного решения применяется gunicorn + nginx

Настройки gunicorn (пример):
::

   # /etc/systemd/system/gunicron.service
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=django
   Group=www-data
   WorkingDirectory=/home/django/GarageBand_bot
   ExecStart=/home/django/GarageBand_bot/venv/bin/gunicorn --access-logfile - --workers 1 --bind unix:/home/django/GarageBand_bot/garage_band_bot.sock garage_band_bot.wsgi

   [Install]
   WantedBy=multi-user.target


Настройки nginx (пример):
::

   # /etc/nginx/sites-available/garage_band_bot
   server {
       listen 8000;
       server_name *.*.*.*;

       location = /favicon.ico {access_log off; log_not_found off; }
       location /static/ {
           root /home/django/GarageBand_bot;
       }
       location /media/ {
           root /home/django/GarageBand_bot;
       }
       location / {
           include proxy_params;
           proxy_pass http://unix:/home/django/GarageBand_bot/garage_band_bot.sock;
       }
   }

После запуска настроенных nginx и gunicorn и настройки фаерволла для порта 8000,
основная админка django с инструментами для правки таблиц БД будет доступна по адресу
http://hostname:8000/admin, просмотрщик логов - по адресу
http://hostname:8000/bot_admin/logs.

Доступ по логину/паролю суперпользователя django.

~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 3
   :caption: Содержание:

   adminapp
   garage_band_bot
   logger
   tgbot
   utils


Указатели и поиск
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
