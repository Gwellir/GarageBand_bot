import os

from checks import (
    check_finish,
    check_misinputs,
    check_name_request,
    check_request_car_type,
    check_request_description,
    check_request_photo,
    check_request_tag,
    check_summary,
    check_welcome,
)
from pytest import mark
from senders import click_button, text_reply
from telethon import TelegramClient

BOT_ID = os.getenv("tested_bot_id")


@mark.asyncio
async def test_posting(client: TelegramClient, image_path, bot_name):
    """Проводит полный функциональный тест постинга заявки в канал."""

    for i in range(1):
        async with client.conversation(bot_name, timeout=5) as conv:

            resp = await text_reply(conv, "/start")

            check_welcome(resp)

            answer = await click_button(conv, resp, "Оформить заявку")

            check_name_request(answer)

            answer = await text_reply(conv, "Владислав")

            check_request_tag(answer)

            answer = await click_button(conv, answer, "Двигатель/ходовая")

            check_request_car_type(answer)

            answer = await text_reply(conv, "Тест 2021 года")

            check_request_description(answer)

            answer = await text_reply(conv, "Автоматическая проверка работы бота")

            check_request_photo(answer)

            answer1 = await text_reply(conv, "Картинка", file=image_path)
            answer2 = await conv.get_response()

            check_summary((answer1, answer2))

            answer = await click_button(conv, answer2, "✅ Публикуем")

            check_finish(answer)


@mark.asyncio
async def test_full(client: TelegramClient, image_path, bot_name):
    """Проводит полный функциональный тест постинга заявки в канал."""

    async with client.conversation(bot_name, timeout=5) as conv:

        stage = 0
        answer = await text_reply(conv, "/start")
        check_welcome(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Оформить заявку")
        check_name_request(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Отменить")
        check_welcome(answer)

        answer = await click_button(conv, answer, "Оформить заявку")
        check_name_request(answer)

        answer = await text_reply(conv, "Владислав")
        check_request_tag(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Отменить")
        check_name_request(answer)

        answer = await text_reply(conv, "Владислав")
        check_request_tag(answer)

        answer = await click_button(conv, answer, "Двигатель/ходовая")
        check_request_car_type(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Отменить")
        check_request_tag(answer)

        answer = await click_button(conv, answer, "Двигатель/ходовая")
        check_request_car_type(answer)

        answer = await text_reply(conv, "Тест 2021 года")
        check_request_description(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Отменить")
        check_request_car_type(answer)

        answer = await text_reply(conv, "Тест 2021 года")
        check_request_description(answer)

        answer = await text_reply(conv, "Автоматическая проверка работы бота")
        check_request_photo(answer)

        answer = await check_misinputs(conv, answer, stage)
        stage += 1

        answer = await click_button(conv, answer, "Отменить")
        check_request_description(answer)

        answer = await text_reply(conv, "Автоматическая проверка работы бота")
        check_request_photo(answer)

        answer1 = await text_reply(conv, "Картинка", file=image_path)
        answer2 = await conv.get_response()
        check_summary((answer1, answer2))

        _, answer = await check_misinputs(conv, answer2, stage)
        stage += 1

        answer = await click_button(conv, answer, "✅ Публикуем")
        check_finish(answer)
