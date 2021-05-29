stages_info = [
    {  # stage 1
        "text": 'Добрый день! Я "GarageBand-бот", помогаю размещать заявки на ремонт для канала '
        'Автосервис Украина.\nНажми ниже кнопочку "Оформить заявку", и приступим — это быстро.',
        "buttons": [
            [
                {
                    "text": "Оформить заявку",
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
        "text": "Представьтесь, пожалуйста, как вас зовут?",
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
        "text": "🛠️ Напишите название заявки — что нужно сделать\n\n"
        "```\nНапример: Ремонт генератора Део Ланос 2007 года\n```",
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
        "text": "🛠️ Расскажите подробнее, чтобы мастер мог оценить объем работы\n\n"
        "```\n- желаемый результат\n"
        "- требования к выполнению работ\n"
        "- требуется дозакупка запчастей, или привезёте самостоятельно\n"
        "- желательно указывать VIN автомобиля или номер кузова, так мастеру "
        "будет проще заказать необходимые комплектующие...\n"
        "```",
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
        "text": "📷 Вы можете добавить фотографии к посту, так будет понятнее\n"
        "_(загрузите изображение или нажмите \"Пропустить\")_",
        "buttons": [
            [
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
        "text": 'Загрузите фото и нажмите "Далее"',
        "buttons": [
            [
                {
                    "text": "Далее",
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
        "text": "📍 В каком городе, районе Вы хотели бы провести ремонт?",
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
        "text": "📞 Укажите свой номер телефона для связи"
                "``` пример формата: +38 097 000 00 00```",
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
        "buttons": [],
    },
]

summary = {
    "text": "*#%s %s*\n\n"  # request.pk, request.title
    "🛠️ %s\n\n"  # request.description
    "📍 %s\n\n"  # request.location
    "🖋 @%s - %s\n\n"  # request.user.username, request.user.get_fullname()
    "📞 %s \t",  # request.phone
    "buttons": [
        [
            {
                "text": "✅ Публикуем",
                "callback_data": "final_confirm",
            },
            {
                "text": "❌ Заново",
                "callback_data": "restart",
            },
        ],
        [
            {
                "text": "Перейти в канал Автосервис Украина",
                "url": "https://t.me/GarageBandKharkov",
            }
        ],
    ],
}
