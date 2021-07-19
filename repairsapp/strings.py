"""Содержит строки шаблонов ответов бота."""

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        "Я Администратор заявок, помогаю размещать заявки на ремонт для канала "
        '<a href="https://t.me/{channel_name}">Автосервис Украина</a>.\n'
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
    {  # stage 3
        "text": "Представьтесь, пожалуйста, как вас зовут?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # stage 4 todo put all strings to db?
        "text": "🛠️ Выберите тип ремонта, который Вам нужен",
        "text_buttons": [
            [
                {
                    "text": "Двигатель/ходовая",
                },
            ],
            [
                {
                    "text": "Кузовной ремонт",
                },
            ],
            [
                {
                    "text": "Автоэлектрика",
                },
            ],
            [
                {
                    "text": "Компьютерная диагностика",
                },
            ],
            [
                {
                    "text": "Нужен совет",
                },
            ],
            [
                {
                    "text": "Другое",
                },
            ],
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {
        "text": "🚘 Какой у вас автомобиль?\n" "Год выпуска, объём мотора?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {
        "text": "🛠️ Расскажите подробнее по работам чтобы мастер смог оценить объем"
        " - что вас беспокоит?\n",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ]
        ],
    },
    {
        "text": "📷 Добавьте фотографию, так будет понятнее\n"
        '<i>(загрузите изображение или нажмите "Пропустить")</i>',
        "text_buttons": [
            [
                {
                    "text": "Пропустить",
                },
            ],
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "text_buttons": None,
    },
    {  # stage finished
        "text": "Благодарим за сотрудничество!\n"
        'Ваша заявка <a href="https://t.me/{channel_name}/{registered_msg_id}">'
        "#{registered_pk}</a> опубликована.\n"
        "После её исполнения Вы можете оставить обратную связь по кнопке "
        '"Оставить отзыв"',
        "buttons": [
            [
                {
                    "text": "Перейти к вашему посту в канале",
                    "url": "https://t.me/{channel_name}/{registered_msg_id}",
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
                    "text": "Оставить отзыв",
                    "callback_data": "leave_feedback {registered_pk}",
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
    "text": "<b>#{request_tag} #{registered_pk}</b>\n\n"
    "🚘 {request_car_type}\n\n"
    "🛠️ {request_desc}\n\n"
    "🖋 {user_name}\n\n",
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
