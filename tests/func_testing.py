import os

from pytest import mark
from telethon import TelegramClient
from telethon.tl.custom.message import Message

BOT_ID = os.getenv("tested_bot_id")


@mark.asyncio
async def test_start(client: TelegramClient, image, bot_name):
    """Проводит полный функциональный тест постинга заявки в канал."""

    for i in range(1):
        async with client.conversation(bot_name, timeout=5) as conv:
            image_file = open(image, "rb")
            await conv.send_message("/start")

            resp: Message = await conv.get_response()

            assert "Я Администратор заявок, помогаю размещать заявки" in resp.raw_text
            assert resp.button_count == 1
            assert resp.buttons[0][0].text == "Оформить заявку"

            await resp.click(text="Оформить заявку")

            answer = await conv.get_response()
            assert answer.button_count == 1
            assert "Представьтесь, пожалуйста" in answer.raw_text
            assert answer.buttons[0][0].text == "Отменить"

            await conv.send_message("Владислав")
            answer = await conv.get_response()

            assert answer.button_count == 7
            assert "Выберите тип ремонта" in answer.raw_text
            assert answer.buttons[0][0].text == "Двигатель/ходовая"
            assert answer.buttons[6][0].text == "Отменить"

            await answer.buttons[0][0].click()
            answer = await conv.get_response()

            assert answer.button_count == 1
            assert "Расскажите, какие работы Вам" in answer.raw_text
            assert answer.buttons[0][0].text == "Отменить"

            await conv.send_message("Автоматическая проверка работы бота")
            answer = await conv.get_response()

            assert answer.button_count == 2
            assert "Добавьте фотографию, так будет" in answer.raw_text
            assert answer.buttons[0][0].text == "Пропустить"
            assert answer.buttons[1][0].text == "Отменить"

            await conv.send_message("Картинка", file=image_file)
            answer = await conv.get_response()

            assert answer.button_count == 1
            assert "В каком городе, районе" in answer.raw_text
            assert answer.buttons[0][0].text == "Отменить"

            await conv.send_message("Санкт-Петербург")

            answer1 = await conv.get_response()
            assert answer1.button_count == 0
            assert "Вы молодец!" in answer1.raw_text

            answer2 = await conv.get_response()
            assert answer2.button_count == 2
            assert "#Двигатель_ходовая" in answer2.raw_text
            assert "🛠️ Автоматическая проверка работы бота" in answer2.raw_text
            assert "📍 Санкт-Петербург" in answer2.raw_text
            assert "Владислав" in answer2.raw_text
            assert answer2.buttons[0][0].text == "✅ Публикуем"
            assert answer2.buttons[0][1].text == "❌ Заново"

            await answer2.buttons[0][0].click()
            answer = await conv.get_response()

            assert answer.button_count == 3
            assert "Благодарим за сотрудничество!" in answer.raw_text
            assert answer.buttons[0][0].text == "Перейти к вашему посту в канале"
            assert answer.buttons[1][0].text == "Оформить ещё заявку"
            assert answer.buttons[2][0].text == "Разместить рекламу"
            image_file.close()
