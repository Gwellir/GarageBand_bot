stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        "Я Администратор заявок, помогаю размещать заявки на ремонт для канала "
        '<a href="https://t.me/GarageBandKharkov">Автосервис Украина</a>.\n'
        'Нажмите "Оформить заявку".',
        "buttons": [
            [
                {
                    "text": "Оформить заявку",
                    "callback_data": "new_request",
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
    {  # stage 4 todo put all strings to db?
        "text": "🛠️ Выберите тип ремонта, который Вам нужен",
        "text_buttons": [
            [
                {
                    "text": "Кузов",
                },
                {
                    "text": "Покраска",
                },
            ],
            [
                {
                    "text": "ТО/Диагностика",
                },
                {
                    "text": "Двигатель/КПП",
                },
            ],
            [
                {
                    "text": "Автоэлектрика",
                },
                {
                    "text": "Салон",
                },
            ],
            [
                {
                    "text": "Ходовая часть",
                },
                {
                    "text": "Шиномонтаж",
                },
            ],
            [
                {
                    "text": "Кондиционер",
                },
                {
                    "text": "Тормозная система",
                },
            ],
            [
                {
                    "text": "Рулевое управление",
                },
                {
                    "text": "Выхлопная система",
                },
            ],
            [
                {
                    "text": "Другое",
                },
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # stage 5
        "text": "🛠️ Расскажите, какие работы Вам требуются:\n"
        "<pre>- какой у вас автомобиль?\n"
        "- год выпуска/объем мотора?\n"
        "- VIN автомобиля или номер Кузова\n"
        "- что именно беспокоит?\n"
        "- желаемый результат\n"
        "- нужна дозакупка запчастей или привезете самостоятельно?\n"
        "- требования к выполнению работ</pre>",
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
        "text": "📷 Добавьте фотографию, так будет понятнее\n"
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
        "text": "📞 Укажите свой номер телефона для связи\n"
        "<i>(ваш телефон не будет виден мастерам)</i>"
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
        "text": "Благодарим за сотрудничество!\n"
        "Ваша заявка #{registered_pk} опубликована.",
        "buttons": [
            [
                {
                    "text": "Перейти в канал Автосервис Украина",
                    "url": "https://t.me/AutoServiceUA",
                }
            ],
            [
                {
                    "text": "Оформить ещё заявку",
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
]

summary = {
    "text": "<b>#{request_tag} #{registered_pk}</b>\n\n"
    "🛠️ {request_desc}\n\n"
    "📍 {request_location}\n\n"
    "🖋 <a href='tg://user?id={user_tg_id}'>{user_name}</a>\n\n",
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
    ],
}

admin = {
    "text": "#request\n<b>Заявка #{registered_pk}</b>\n"
    "От: <a href='tg://user?id={user_tg_id}'>{user_name}</a>",
    "buttons": [
        [
            {
                "text": "❌ Удалить",
                "callback_data": "admin_delete {registered_msg_id}",
            }
        ],
        [
            {
                "text": "☠️ Забанить пользователя",
                "callback_data": "admin_ban {user_pk}",
            }
        ],
    ],
}
