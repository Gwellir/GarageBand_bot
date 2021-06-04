stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        'Я "GarageBand-бот", помогаю размещать заявки на ремонт для канала '
        '<a href="https://t.me/GarageBandKharkov">Автосервис Украина</a>.\n'
        'Нажми ниже кнопочку "Оформить заявку", и приступим — это быстро.',
        "buttons": [
            [
                {
                    "text": "Оформить заявку",
                    "callback_data": "new_request",
                },
            ],
            [
                {
                    "text": "Разместить рекламу",
                    "url": "https://t.me/ZhitkovArtem",
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
        "<pre>Например: Ремонт генератора Део Ланос 2007 года</pre>",
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
        "<pre>- желаемый результат\n"
        "- требования к выполнению работ\n"
        "- требуется дозакупка запчастей, или привезёте самостоятельно\n"
        "- желательно указывать VIN автомобиля или номер кузова, так мастеру "
        "будет проще заказать необходимые комплектующие...</pre>",
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
        "text": "📷 Вы можете добавить фотографию к посту, так будет понятнее\n"
        '<i>(загрузите изображение или нажмите "Пропустить")</i>',
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
        "<pre> пример формата: +38 097 000 00 00</pre>",
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
    "text": "<b>#%s %s</b>\n\n"  # request.pk, request.title
    "🛠️ %s\n\n"  # request.description
    "📍 %s\n\n"  # request.location
    "🖋 <a href='tg://user?id=%s'>%s</a>\n\n"  # request.user.user_id request.user.name
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

admin = {
    "text": "#request\n<b>Заявка #%s</b>\n"  # request.registered.pk
    "От: <a href='tg://user?id=%s'>%s</a>",  # request.user.user_id request.user.name
}
