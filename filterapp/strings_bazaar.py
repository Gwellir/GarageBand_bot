"""Содержит строки шаблонов ответов бота."""

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        'Я "Базар Фильтр Бот", помогаю осуществлять поиск объявлений на продажу'
        ' авто для канала <a href="https://t.me/{channel_name}">ОП Базар</a>.\n'
        'Нажмите "Создать фильтр".',
        "buttons": [
            [
                {
                    "text": "Создать фильтр",
                    "callback_data": "new_request",
                },
            ],
        ],
    },
    # {  # stage 2
    #     "text": 'Если вы ещё не подписаны на канал '
    #     '<a href="https://t.me/{channel_name}">ОП Базар</a>, '
    #     'то перейдите и подпишитесь. Затем нажмите "Далее".',
    #     "text_buttons": [
    #         [
    #             {
    #                 "text": "Далее",
    #             },
    #         ],
    #         [
    #             {
    #                 "text": "Отменить",
    #             }
    #         ]
    #     ]
    # },
    {
        "text": "Выберите интересующие диапазоны цен:",
        "attr_choices": "price_ranges",
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
            ]
        ],
    },
    {
        "text": "Выберите интересующие регионы:",
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
            ]
        ],
    },
    {  # stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "text_buttons": None,
    },
    {  # stage done
        "text": "Ваш фильтр #{registered_pk} зарегистрирован:\n\n"
        "💲 {filter_price_ranges}\n\n"
        "📍 {filter_regions}\n\n",
        "buttons": [
            [
                {
                    "text": "Создать ещё фильтр",
                    "callback_data": "new_request",
                },
            ]
        ],
    },
]

summary = {
    "text": "<b>Фильтр</b>\n\n"
    "💲 {filter_price_ranges}\n\n"
    "📍 {filter_regions}\n\n",
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
    "text": "<b>Результаты</b>:\n\n"
    ""
}