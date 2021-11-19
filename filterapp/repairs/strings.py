"""Содержит строки шаблонов ответов бота."""
from garage_band_bot import settings

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        'Я "Автосервис Фильтр Бот", помогаю осуществлять поиск и отслеживание заявок'
        ' на ремонт машин для канала <a href="https://t.me/{channel_name}">'
        "Автосервис Украина</a>.\n"
        "После настройки фильтра все заявки, подпадающие под его параметры, "
        "будут дублироваться вам в приват.\n\n"
        'Нажмите "Настроить фильтр".',
        "buttons": [
            [
                {
                    "text": "Настроить фильтр",
                    "callback_data": "new_request",
                },
            ],
        ],
    },
    {  # stage 2
        "text": "Если вы по какой-то причине не подписаны на канал "
        '<a href="https://t.me/{channel_name}">Автосервис Украина</a>, '
        'то перейдите по ссылке и подпишитесь. Затем нажмите "Далее".',
        "text_buttons": [
            [
                {
                    "text": "Далее",
                },
            ],
            [
                {
                    "text": "Отменить",
                }
            ],
        ],
    },
    {
        "text": "Выберите интересующие типа ремонтов и затем нажмите 'Далее':",
        "attr_choices": "repair_types",
        "text_buttons": [
            [
                {
                    "text": "Далее",
                }
            ],
            [
                {
                    "text": "Отменить",
                }
            ],
        ],
    },
    {
        "text": 'Выберите интересующие регионы и затем нажмите "Далее":',
        "attr_choices": "regions",
        "text_buttons": [
            [
                {
                    "text": "Далее",
                },
            ],
            [
                {
                    "text": "Отменить",
                }
            ],
        ],
    },
    {
        "text": "<b>Подписка</b>\nНа данный момент: {sub_active} до {expiry_date}",
        "text_buttons": [
            [
                {
                    "text": "Далее",
                },
            ],
            [
                {
                    "text": "Оплатить",
                }
            ],
            [
                {
                    "text": "Отменить",
                }
            ],
        ],
    },
    {
        "text": "Оплатите подписку по ссылке",
        "buttons": [
            [
                {
                    "text": "Оплатить",
                    "url": "{checkout_url}",
                },
            ],
        ],
    },
    {  # stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "text_buttons": None,
    },
    {  # stage done
        "text": "Ваш фильтр настроен:\n\n" "🛠️ {repair_types}\n\n" "📍 {regions}\n\n",
        "buttons": [
            [
                {
                    "text": "Перенастроить фильтр",
                    "callback_data": "new_request",
                },
            ]
        ],
    },
]

summary = {
    "text": "<b>Фильтр</b>\n\n" "🛠️ {repair_types} \n\n" "📍 {regions}\n\n",
    "buttons": [
        [
            {
                "text": "✅ Готово",
                "callback_data": "final_confirm {filter_pk}",
            },
            {
                "text": "❌ Заново",
                "callback_data": "restart",
            },
        ],
    ],
}

results = {
    "text": "<b>Десятка самых свежих результатов " "за последние три дня</b>:\n" ""
}

payment = {
    "title": "Подписка на месяц",
    "description": 'Месячная оплата подписки на канал "Автосервис Украина"',
    "payload": "Repairs-Filter-payment",
    "provider_token": settings.PROVIDER_TOKEN,
    "currency": "UAH",
    "price": 10,
}
