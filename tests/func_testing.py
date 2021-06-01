import os

from pytest import mark
from telethon import TelegramClient
from telethon.tl.custom.message import Message
from time import sleep

BOT_ID = os.getenv("tested_bot_id")


@mark.asyncio
async def test_start(client: TelegramClient):
    async with client.conversation("@GarageBandTest_bot", timeout=5) as conv:
        await conv.send_message("/start")

        resp: Message = await conv.get_response()

        assert "помогаю размещать заявки" in resp.raw_text
        assert resp.button_count == 3
        assert resp.buttons[0][0].text == "Оформить заявку"
        assert resp.buttons[1][0].text == "Поиск заявок"
        assert resp.buttons[1][1].text == "Разместить рекламу"

        await resp.click(text="Оформить заявку")
        answer = await conv.get_response()
        assert answer.button_count == 2
        assert "создать новую заявку" in answer.raw_text
        assert answer.buttons[0][0].text == "Начать оформление"
        assert answer.buttons[1][0].text == "Отменить"

        await answer.click(text="Начать оформление")
        answer = await conv.get_response()
        assert answer.button_count == 1
        assert "Представьтесь, пожалуйста" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("Владислав")
        answer = await conv.get_response()

        assert answer.button_count == 1
        assert "название заявки" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("Автотест")
        answer = await conv.get_response()

        assert answer.button_count == 1
        assert "Расскажите подробнее" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("Автоматическая проверка работы бота")
        answer = await conv.get_response()

        assert answer.button_count == 2
        assert "Вы можете добавить фотографии" in answer.raw_text
        assert answer.buttons[0][0].text == "Пропустить"
        assert answer.buttons[1][0].text == "Отменить"

        await answer.click(text="Пропустить")
        answer = await conv.get_response()

        assert answer.button_count == 1
        assert "В каком городе, районе" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("Санкт-Петербург")
        answer = await conv.get_response()

        assert answer.button_count == 1
        assert "Укажите свой номер телефона" in answer.raw_text
        assert answer.buttons[0][0].text == "Отменить"

        await conv.send_message("+38 097 000 00 00")
        answer1 = await conv.get_response()
        assert answer1.button_count == 0
        assert "Вы молодец!" in answer1.raw_text

        answer2 = await conv.get_response()
        assert answer2.button_count == 3
        assert "Автотест" in answer2.raw_text
        assert "🛠️ Автоматическая проверка работы бота" in answer2.raw_text
        assert "📍 Санкт-Петербург" in answer2.raw_text
        assert "🖋 @Valion - Владислав" in answer2.raw_text
        assert "📞 +380970000000" in answer2.raw_text
        assert answer2.buttons[0][0].text == "✅ Публикуем"
        assert answer2.buttons[0][1].text == "❌ Заново"
        assert answer2.buttons[1][0].text == "Перейти в канал Автосервис Украина"

        await answer2.buttons[0][0].click()
        answer = await conv.get_response()

        assert answer.button_count == 0
        assert "Благодарим за сотрудничество!" in answer.raw_text
