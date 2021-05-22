stages_info = [
    {  # stage 1
        "text": "Здравствуйте, Вы обратились в службу приёма заявок Garage Band.\nВыберите действие:",
        "buttons": [
            [
                {
                    "text": "Создать новую заявку",
                    "callback_data": "new_request",
                },
            ],
            [
                {
                    "text": "Поиск заявок",
                    "callback_data": "search_request",
                },
                {
                    "text": "Разместить рекламу",
                    "callback_data": "propose_ads",
                },
            ],
        ],
    },
    {  # stage 2
        "text": "Вы собираетесь создать новую заявку на обслуживание.\nПродолжить?",
        "buttons": [
            [
                {
                    "text": "Начать оформление",
                    "callback_data": "stage2_confirm",
                },
            ],
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ],
        ],
    },
    {  # stage 3
        "text": "Представьтесь, пожалуйста",
        "buttons": [
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ],
        ],
    },
    {  # stage 4
        "text": "Напишите название заявки - что нужно сделать",
        "buttons": [
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ]
        ],
    },
    {  # stage 5
        "text": "Расскажите подробнее, чтобы мастер мог оценить объем работы",
        "buttons": [
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ]
        ],
    },
    {  # stage 6
        "text": "Вы можете добавить к посту фотографии, так будет понятнее",
        "buttons": [
            [
                {
                    "text": "Добавить",
                    "callback_data": "have_photos",
                },
                {
                    "text": "Пропустить",
                    "callback_data": "skip_photos",
                },
            ],
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ],
        ],
    },
    {  # stage 7
        "text": 'Загрузите фото, когда закончите - нажмите "Следующий этап"\n(отправляйте файлы по одному)',
        "buttons": [
            [
                {
                    "text": "Следующий этап",
                    "callback_data": "photos_confirm",
                },
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ]
        ],
    },
    {  # stage 8
        "text": "В каком городе, районе Вы хотели бы провести ремонт?",
        "buttons": [
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ]
        ],
    },
    {  # stage 9
        "text": "Укажите свой номер телефона для связи",
        "buttons": [
            [
                {
                    "text": "Отменить",
                    "callback_data": "restart",
                },
            ]
        ],
    },
    {  # stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "buttons": [],
    },
    {  # stage finished
        "text": "Благодарим за сотрудничество!\nВаша заявка опубликована.",
        "buttons": [
            [
                {
                    "text": "Начать заново",
                    "callback_data": "restart",
                },
            ]
        ],
    },
]

summary = {
    "text": "Задание: %s\n\nПодробнее: %s\n\nТелефон: %s\nTG: %s",
    "buttons": [
        [
            {
                "text": "Зарегистрировать",
                "callback_data": "final_confirm",
            },
            {
                "text": "Отменить",
                "callback_data": "restart",
            },
        ]
    ],
}
