from pathlib import Path

from senders import text_reply

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "tests/clouds-mf.jpg"
STICKER_PATH = BASE_DIR / "tests/sticker.webp"


def check_welcome(answer):
    assert "Я Администратор заявок, помогаю размещать заявки" in answer.raw_text
    assert answer.button_count == 1
    assert answer.buttons[0][0].text == "Оформить заявку"


def check_name_request(answer):
    assert answer.button_count == 1
    assert "Представьтесь, пожалуйста" in answer.raw_text
    assert answer.buttons[0][0].text == "Отменить"


def check_request_tag(answer):
    assert answer.button_count == 7
    assert "Выберите тип ремонта" in answer.raw_text
    assert answer.buttons[0][0].text == "Двигатель/ходовая"
    assert answer.buttons[6][0].text == "Отменить"


def check_request_car_type(answer):
    assert answer.button_count == 1
    assert "🚘 Какой у вас автомобиль?" in answer.raw_text
    assert answer.buttons[0][0].text == "Отменить"


def check_request_description(answer):
    assert answer.button_count == 1
    assert "🛠️ Расскажите подробнее по работам чтобы мастер смог" in answer.raw_text
    assert answer.buttons[0][0].text == "Отменить"


def check_request_photo(answer):
    assert answer.button_count == 2
    assert "Добавьте фотографию, так будет" in answer.raw_text
    assert answer.buttons[0][0].text == "Пропустить"
    assert answer.buttons[1][0].text == "Отменить"


def check_summary(answers):
    answer1, answer2 = answers
    assert answer1.button_count == 0
    assert "Вы молодец!" in answer1.raw_text

    assert answer2.button_count == 2
    assert "#Двигатель_ходовая #000" in answer2.raw_text
    assert "🛠️ Автоматическая проверка работы бота" in answer2.raw_text
    assert "🚘 Тест 2021 года" in answer2.raw_text
    assert "🖋 Владислав" in answer2.raw_text
    assert answer2.buttons[0][0].text == "✅ Публикуем"
    assert answer2.buttons[0][1].text == "❌ Заново"


def check_finish(answer):
    assert answer.button_count == 3
    assert "Благодарим за сотрудничество!" in answer.raw_text
    assert answer.buttons[0][0].text == "Перейти к вашему посту в канале"
    assert answer.buttons[1][0].text == "Оформить ещё заявку"
    assert answer.buttons[2][0].text == "Разместить рекламу"


def check_same_reply(answer, warning):
    assert answer.raw_text == warning.raw_text
    assert answer.button_count == warning.button_count


async def send_short_text(conv):
    warning = await text_reply(conv, "A")
    check_too_short(warning)
    return await conv.get_response()


async def send_any_picture(conv):
    warning = await text_reply(conv, "Картинка", file=IMAGE_PATH)
    check_not_text(warning)
    return await conv.get_response()


async def send_sticker(conv):
    warning = await text_reply(conv, "", file=STICKER_PATH)
    check_not_image(warning)
    return await conv.get_response()


async def send_long_text(conv):
    warning = await text_reply(conv, "A" * 2000)
    check_too_long(warning)
    return await conv.get_response()


async def send_misinputs_for_welcome(conv):
    answer = await text_reply(conv, "Тест")
    check_welcome(answer)
    answer = await text_reply(conv, "Тест", file=IMAGE_PATH)
    check_welcome(answer)
    answer = await text_reply(conv, "Тест", file=STICKER_PATH)
    check_welcome(answer)
    return answer


async def send_misinputs_for_picture(conv):
    warning = await text_reply(conv, "Тест")
    check_not_image(warning)
    answer = await conv.get_response()
    check_request_photo(answer)
    warning = await text_reply(conv, "Тест", file=STICKER_PATH)
    check_not_image(warning)
    answer = await conv.get_response()
    check_request_photo(answer)
    return answer


async def send_misinputs_for_summary(conv):
    warning = await text_reply(conv, "Тест")
    check_not_button(warning)
    answers = await conv.get_response(), await conv.get_response()
    check_summary(answers)
    warning = await text_reply(conv, "Тест", file=IMAGE_PATH)
    check_not_button(warning)
    answers = await conv.get_response(), await conv.get_response()
    check_summary(answers)
    warning = await text_reply(conv, "Тест", file=STICKER_PATH)
    check_not_button(warning)
    answers = await conv.get_response(), await conv.get_response()
    check_summary(answers)
    return answers


MISINPUT_LIST = [
    [send_misinputs_for_welcome],
    [send_short_text, send_long_text, send_any_picture],
    [send_any_picture],
    [send_short_text, send_long_text, send_any_picture],
    [send_short_text, send_long_text, send_any_picture],
    [send_misinputs_for_picture],
    [send_misinputs_for_summary],
    [],
]

STAGE_CHECKS_LIST = [
    check_welcome,
    check_name_request,
    check_request_tag,
    check_request_car_type,
    check_request_description,
    check_request_photo,
    check_summary,
    check_finish,
]


async def check_misinputs(conv, answer, stage):
    reply = answer
    for misinput in MISINPUT_LIST[stage]:
        reply = await misinput(conv)
        STAGE_CHECKS_LIST[stage](reply)
    return reply


def check_too_short(answer):
    assert answer.button_count == 0
    assert "Слишком короткий ответ, введите не менее" in answer.raw_text


def check_too_long(answer):
    assert answer.button_count == 0
    assert "Превышена максимальная длина ответа (" in answer.raw_text


def check_not_text(answer):
    assert answer.button_count == 0
    assert "Запрошенный текст не введён!" in answer.raw_text


def check_not_image(answer):
    assert answer.button_count == 0
    assert "Запрошенное изображение не загружено!" in answer.raw_text


def check_not_button(answer):
    assert answer.button_count == 0
    assert "Ожидается нажатие на кнопку!" in answer.raw_text
