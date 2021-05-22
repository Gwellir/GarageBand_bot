stages_info = [
    {  # stage 1
        'text': "Здравствуйте, Вы обратились в службу приёма заявок Garage Band.\nВыберите действие:",
        'buttons': [
            [
                {
                    'text': "Создать новую заявку",
                    'callback_data': 'new_request',
                },
            ],
            [
                {
                    'text': "Поиск заявок",
                    'callback_data': 'search_request',
                },
                {
                    'text': "Разместить рекламу",
                    'callback_data': 'propose_ads',
                },
            ],
        ],
    },
    {  # stage 2
        'text': "Вы собираетесь создать новую заявку на обслуживание.\nПродолжить?",
        'buttons': [
            [
                {
                    'text': "Начать оформление",
                    'callback_data': 'stage2_confirm',
                },
            ],
            [
                {
                    'text': "Отменить",
                    'callback_data': 'restart',
                },
            ],
        ],
    },
    {  # stage 3
        'text': "Представьтесь, пожалуйста",
        'buttons': [
            [
                {
                    'text': "Отменить",
                    'callback_data': 'restart',
                },
            ],
        ],
    },
    {  # stage 4
        'text': 'Напишите название заявки - что нужно сделать',
        'buttons': [
            [
                {
                    'text': "Отменить",
                    'callback_data': 'restart',
                },
            ]
        ]
    }
]