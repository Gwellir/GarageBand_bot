"""Содержит строки шаблонов ответов бота."""

stages_info = [
    {  # stage 1
        "text": "Здравствуйте!\n"
        'Я "Автобазар Бот", помогаю размещать объявления на продажу авто для канала '
        '<a href="https://t.me/{channel_name}">ОП Базар</a>.\n'
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
        "text": "📞 Укажите ваш номер телефона",
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
        "text": "🎛 Укажите пробег автомобиля, тыс. км",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 7
        "text": "💸 Укажите точную цену, $ \n\n",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ]
        ],
    },
    {  # 8
        "text": "Цена с торгом или нет?",
        "text_buttons": [
            [{"text": "Торг"}, {"text": "Без торга"}],
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 9
        "text": "🛠️ Добавьте полное описание продажи\n"
        "<i>(не более 750 символов)</i>\n\n"
        "<pre>- техническое состояние\n- комплектация</pre>",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ]
        ],
    },
    {  # 10
        "text": "{photos_loaded}📷 Добавьте фотографии\n"
        "Первая фотография будет использована для оформления поста в канале, "
        "остальные размещаются в комментариях.\n"
        '<i>загрузите не более 9 изображений и/или нажмите "Далее"</i>',
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
    {  # 11
        "text": "📍 В каком городе продается автомобиль?",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # confirm
        "text": "📍 Вы указали местоположение:\n"
        "<b>{location}</b>\n\n"
        "Подтвердите, нажав кнопку ниже.\n"
        '<pre>В случае проблем - нажмите "Отменить" и'
        " укажите ближайший более крупный город.</pre>",
        "confirm_choices": "location_selection",
        "text_buttons": [
            [
                {
                    "text": "Отменить",
                },
            ],
        ],
    },
    {  # 12 stage confirmation
        "text": "Вы молодец! Смотрите, что у нас получилось:",
        "text_buttons": None,
    },
    {  # 13 stage finished
        "text": "Благодарим за сотрудничество!\n"
        'Ваше объявление <a href="https://t.me/{channel_name}/{registered_msg_id}">'
        "#{registered_pk}</a> опубликовано.\n\n"
        "Не забудьте закрыть заявку после продажи автомобиля.\n"
        "(это может занять несколько секунд)",
        "buttons": [
            [
                {
                    "text": "Разместить ещё объявление",
                    "callback_data": "new_request",
                },
            ],
            [
                {
                    "text": "Перейти к вашему объявлению в канале",
                    "url": "https://t.me/{channel_name}/{registered_msg_id}",
                }
            ],
            [
                {
                    "text": "Снять Авто с продажи",
                    "callback_data": "complete {registered_pk}",
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
    {  # stage 14
        "text": 'Ваше объявление #{registered_pk} переведено в статус "ПРОДАНО"',
        "buttons": [
            [
                {
                    "text": "Разместить ещё объявление",
                    "callback_data": "new_request",
                },
            ]
        ],
    },
]

summary = {
    "text": "<b>#{registered_pk}</b>\n\n"
    "#{ad_price_range}\n\n"
    "🚘 {car_type}\n\n"
    "{desc}\n\n"
    "🎛 Пробег {ad_mileage} тыс. км\n\n"
    "💸 Цена <b>${ad_price}</b> {ad_bargain_string}\n\n"
    "📍 {location} #{region}\n\n"
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

summary_sold = {
    "text": "<b>[ ПРОДАНО ]</b>\n\n"
    "<b>#{registered_pk}</b>\n\n"
    "{ad_price_range}\n\n"
    "🚘 {car_type}\n\n"
    "{desc}\n\n"
    "🎛 Пробег {ad_mileage} тыс. км\n\n"
    "<s>💸 Цена <b>${ad_price}</b> {ad_bargain_string}</s>\n\n"
    "<s>📍 {location} {region}</s>\n\n"
    "📞 {user_name}\n\n",
    "text_buttons": None,
}

summary_forward = {
    "text": "<b>#{registered_pk}</b>\n\n"
    "#{ad_price_range}\n\n"
    "🚘 {car_type}\n\n"
    "{desc}\n\n"
    "🎛 Пробег {ad_mileage} тыс. км\n\n"
    "💸 Цена <b>${ad_price}</b> {ad_bargain_string}\n\n"
    "📍 {location} #{region}\n\n"
    "🖋 {user_name} {user_phone}\n\n",
    "buttons": [
        [
            {
                "text": "Перейти в канал",
                "url": "https://t.me/{channel_name}/{registered_msg_id}",
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

renewal = {
    "text": "Напоминаем, что Ваше объявление "
    '<a href="https://t.me/{channel_name}/{registered_msg_id}">#{registered_pk}</a> '
    "было размещено три недели назад.\nЕсли требуется, отсюда Вы можете запостить его"
    " заново, либо отметить машину проданной.\n\n"
    "<b>Подробности:</b>\n"
    "🚘 {car_type}\n💸 Цена <b>${ad_price}</b>",
    "buttons": [
        [
            {
                "text": "Машина продана",
                "callback_data": "complete {registered_pk}",
            }
        ],
        [
            {
                "text": "Разместить заново",
                "callback_data": "renew {registered_pk}",
            }
        ],
    ],
}
