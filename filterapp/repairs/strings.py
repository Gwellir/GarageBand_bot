"""Содержит строки шаблонов ответов бота."""
from garage_band_bot import settings

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        "Я помогаю настроить сортировку запросов по городам и видам ремонта для канала"
        ' <a href="https://t.me/{channel_name}">Автосервис Украина</a>.\n'
        "После настройки фильтра все заявки, подпадающие под его параметры, "
        "будут дублироваться вам в приват.\n\n"
        'Нажмите "Сформировать фильтр".',
        "buttons": [
            [
                {
                    "text": "Сформировать фильтр",
                    "callback_data": "new_request",
                },
            ],
        ],
    },
    {  # stage 2
        "text": "Для того, чтобы получать уведомления от бота, пожалуйста, подпишитесь"
        ' на канал <a href="https://t.me/{channel_name}">'
        'Автосервис Украина</a>.\nЗатем нажмите "Далее".',
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
        "text": "Укажите название вашей компании или свое имя - так мы назовем вашу форму.",
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
        ]
    },
    {
        "text": "Выберите тип заявок на ремонт, которые вы будете отслеживать,"
        " а затем нажмите 'Далее':",
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
        "text": "Ваш личный фильтр настроен:\n\n"
        "🛠️ {repair_types}\n\n"
        "📍 {regions}\n\n",
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

payment_confirmed = {
    "text": "<b>Оплата подписки проведена.</b>",
    "text_buttons": [
        [{"text": "Далее"}],
        [
            {
                "text": "Отменить",
            }
        ],
    ],
}

payment_denied = {
    "text": "<b>К сожалению, оплата подписки не прошла!</b>"
            "<br>"
            "Пожалуйста, попробуйте ещё раз позже, либо измените платёжное средство.",
    "text_buttons": [
        [{"text": "Далее"}],
    ],
}

