"""Содержит строки шаблонов ответов бота."""

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        'Я "Автобазар Бот", помогаю размещать объявления на продажу авто для канала '
        '<a href="https://t.me/{channel_name}">Автобазар</a>.\n'
        'Нажмите "Разместить объявление".',
        "buttons": [
            [
                {
                    "text": "Разместить объявление",
                    "callback_data": "new_request",
                },
            ],
        ],
    },
    {  # stage 2
        "text": "Представьтесь, пожалуйста, как вас зовут?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # stage 3
        "text": "Укажите ваш номер телефона",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 4
        "text": "🚘 Какой у вас автомобиль?\n" "Год выпуска, объём мотора?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 5
        "text": "🎛 Укажите пробег автомобиля, км",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 6
        "text": "💰 Выберите ценовую категорию продажи",
        "text_buttons": [
            [
                {
                    "text": "до $1000",
                },
                {
                    "text": "от $1000 до $2500",
                },
            ],
            [
                {
                    "text": "от $2500 до $5000",
                },
                {
                    "text": "от $5000 до $7500",
                },
            ],
            [
                {
                    "text": "от $7500 до $10000",
                },
                {
                    "text": "более $10000",
                },
            ],
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 7
        "text": "💸 Укажите точную цену\n<pre>Торг или без?\nВалюта: грн, 💲</pre>",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ]
        ],
    },
    {  # 8
        "text": "🛠️ Добавьте полное описание продажи\n"
        "<pre>- техническое состояние\n- комплектация</pre>",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ]
        ],
    },
    {  # 9
        "text": "📷 Добавьте фотографии\n"
        '<i>(загрузите одно или несколько изображений или нажмите "Далее")</i>',
        "text_buttons": [
            [
                {
                    "text": "Далее",
                },
            ],
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 10
        "text": "📍 В каком городе продается автомобиль?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 11 stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "text_buttons": None,
    },
    {  # 12 stage finished
        "text": "Благодарим за сотрудничество!\n"
        'Ваше объявление <a href="https://t.me/{channel_name}/{registered_msg_id}">'
        "#{registered_pk}</a> опубликовано.\n",
        "buttons": [
            [
                {
                    "text": "Перейти к вашему объявлению в канале",
                    "url": "https://t.me/{channel_name}/{registered_msg_id}",
                }
            ],
            [
                {
                    "text": "Разместить ещё объявление",
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
    {  # stage feedback
        "text": "Заявка #{registered_pk}\n\n"
        "Напишите имя/аккаунт мастера, который проводил работы, "
        "и ваши общие ощущения от проведённых работ.",
        "text_buttons": None,
    },
    {  # stage feedback done
        "text": "Спасибо за обратную связь!",
        "buttons": [
            [
                {
                    "text": "Оформить ещё заявку",
                    "callback_data": "new_request",
                },
            ],
        ],
    },
]

summary = {
    "text": "<b>#{registered_pk}</b>\n\n"
    "#{ad_price_range} {ad_car_type}\n\n"
    "🚘 {ad_desc}\n\n"
    "🎛 Пробег {ad_mileage} км\n\n"
    "💸 Цена <b>{ad_price}</b>\n\n"
    "📍 {ad_location}\n\n"
    "🖋 {user_name} {user_phone}\n\n",
    "buttons": [
        [
            {
                "text": "✅ Публикуем",
                "callback_data": "final_confirm {request_pk}",
            },
            {
                "text": "❌ Заново",
                "callback_data": "restart",
            },
        ],
    ],
}

feedback = {
    "text": "<b>Отзыв клиента по заявке "
    '<a href="https://t.me/{channel_name}/{registered_msg_id}">'
    "#{registered_pk}</a></b>"
    "\n\n"
    "<i>{registered_feedback}</i>"
}

admin = {
    "text": "#ad\n<b>Объявление #{registered_pk}</b>\n"
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
