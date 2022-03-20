### Основная информация о конкретной реализации

Запуск бота осуществляется в режиме polling через модуль [tgbot.apps](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/apps.py#L120)
Django-приложения `tgbot`, при загрузке веб-сервера посредством связки с `gunicorn`. 

При запуске производится загрузка параметров ботов (токенов и id каналов/групп) 
и их привязок к модулям соответствующих заявок из БД,
инициализированные апдейтеры ботов python-telegram-bot помещаются в переменную `tg_updaters`.
(Реализована возможность использовать для получения апдейтов вебхуки, 
но на данный момент не написан роутинг для множественных ботов)

Все боты работают в рамках одного скрипта (вместе с вебсервером), написаны как отдельные Django apps.
Каждый из них направляет свои апдейты в структуру хендлеров по фильтрам, определённую в [tgbot.bot.dispatcher](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/bot/dispatcher.py#L22),
и [tgbot.bot.handlers](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/bot/handlers.py)

Основная точка входа для пользовательских сообщений - [message_handler()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/bot/handlers.py#L286).
Здесь производится извлечение значимых данных бота, пользователей и сообщений и передача их в [обработчик диалогов](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/convoapp/dialog_state_machine.py#L29).

Обработчик диалогов подгружает соответствующие модели пользователей ([tgbot.models.BotUser](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/models.py#L113)) 
и заявок (например, [bazaarapp.models.SaleAd](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/models.py#L128)),
и прикрепляет их к диалогу [convoapp.models.Dialog](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/convoapp/models.py#L9).
Модель диалога реализует унификацию работы со всеми типами заявок, они вызываются через атрибут `.bound`,
который скрывает связь с конкретными back-reference полями, типа `.bound_workrequest`, `.bound_salead`, и т. д.

Затем, в соответствии со стадией диалога, которая хранится в связанной модели (например, [bazaarapp.models.SaleAdStage](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/models.py#L87)),
подгружается процессор обработки ввода от пользователя из модуля [processors](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/processors.py) 
соответствующего приложения или базового модуля [convoapp.processors](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/convoapp/processors.py)

Процессоры подготавливают и записывают данные пользователя в модель заявки, а также в словарь данных модели ([data_as_dict()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/models.py#L201))
В случае ввода несовместимых данных, процессор выбрасывает конкретное исключение, например, [tgbot.exceptions.TextNotProvidedError](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/exceptions.py#L67),
текст которого возвращается пользователю отдельным сообщением.

На базе этого словаря и шаблона ответа обработчик диалогов формирует сообщения-ответы и возвращает их в message_handler 
(исторически шаблоны хранятся сырым текстом в модулях strings, [например](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/strings.py)).
message_handler вызывает функцию [tgbot.bot.senders.send_messages_return_ids()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/strings.py) 
для отправки сообщения в Telegram.

### Процесс проведения заявки 

При контакте с ботом, у которого для данного пользователя нет заявки в процессе обработки, он выдает приглашение 
оформить соответствующую заявку. Затем заводится соответствующий заявке объект.
Пользователь может перемещаться вперёд и назад (на случай ошибки ввода) по стадиям оформления.
Перед финальным размещением поста в привязанном канале пользователю предлагается его (поста) превью.
В случае отказа на данном этапе, заявка будет помечена флагом `is_discarded`, в случае согласия - `is_complete`.

Размещаемому в канале посту соответствует отдельный объект, например [RegisteredAd](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/models.py#L463).
Заявке может принадлежать несколько постов, это используется в случае повторных размещений необслуженных заявок.

Данные поста в канале сохраняются на случай, например, если потребуется дополнить пост фидбеком [convoapp.processors.FeedbackInputProcessor](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/convoapp/processors.py#L255),
или пометить объявление закрытым [SaleAd.set_sold()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/bazaarapp/models.py#L379).
Для этого также предусмотрена возможность подгрузки старой (`is_complete`) заявки [Dialog.get_or_create()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/convoapp/models.py#L34),
после закрытия объявления заявка получит флаг `is_locked`.
В случае, если требуется подгрузить дополнительные данные в привязанную (для обсуждения) группу 
сразу после размещения поста в канале, используется отдельный [post_handler()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/bot/handlers.py#L68),

### Дополнительный функционал

В качестве отдельных ботов реализованы решения для фильтрации поступающих заявок, оформление фильтра происходит аналогично,
а при размещении новых заявок вызывается метод [.trigger_send()](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/filterapp/models.py#L140)
соответствующей модели фильтра.

Существует базовый функционал временных подписок на сервисы (приложение `subscribeapp`), но на данный момент 
он не используется в продакшене.

Модуль handlers также содержит простые обработки /команд для размещения особых постов (инвойс для пожертвований, реклама)
и администраторских действий.

Соблюдение рейт-лимитов телеграма (с учётом размещения наборов фотографий, это иногда становилось проблемой), выполняется
через стандартное решение python-telegram-bot, кастомный класс [MessageQueueBot](https://github.com/Gwellir/GarageBand_bot/blob/8fb22ce1389c97f8417b09682ae4250dc8ee408f/tgbot/bot/queue_bot.py#L5).

### Примерная ранняя схема модулей проекта

(OUTDATED)
[Диаграмма на Draw.io](https://drive.google.com/file/d/1SbxBP3sNaEM7xoTL8wtDtv5ln30GQQq1/view) (нажать кнопку "Открыть в приложении")