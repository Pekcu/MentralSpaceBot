#GigaChat
from aiohttp.web_fileresponse import content_type
from langchain.schema import HumanMessage, SystemMessage
from langchain_gigachat.chat_models.gigachat import GigaChat

#TeleBot libs
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command

#other libs
import asyncio
import json
import logging
import sys

#local libs
from notProject import JokeGenerator
from mentalResponse import MentalResponse

# Получаем ключ телеграм и сбер API
with open("api_config.json") as api_config:
    config = json.load(api_config)
    token = config["bot_api_token"]
    sber_aut = config["sber_aut"]

# Уровень логирования 20 (2/5)
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=token)
# Диспетчер
dp = Dispatcher()


giga = GigaChat(
        # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
        credentials=sber_aut,
        verify_ssl_certs=False,
    )

kb_start = [
        [
           types.KeyboardButton(text="Хочу поддержку🙁")
        ],
        [
            types.KeyboardButton(text="Хочу анекдот"),
            types.KeyboardButton(text="Нужна помощь!")
        ],
    ]

class UserState(StatesGroup):
    waiting_for_response = State()

#базовый хэндлер при старте бота
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    markup = types.ReplyKeyboardMarkup(keyboard=kb_start, resize_keyboard=True)
    await message.answer("Привет, я бот, пока умею только анекдот, хочешь анекдот?",reply_markup=markup)

#хэндлер показывает возможности бота
@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer("не сейчас")

#хэндлер для генерации анекдота
@dp.message(F.text == "Хочу анекдот")
async def cmd_joke(message: types.Message) -> None:
    ranom_joke = await JokeGenerator.randomJoke()
    await message.answer(str(ranom_joke))

#переход на сайт к проф-помощи через ответ.
@dp.message(F.text == "Нужна помощь!")
async def cmd_mental_help(message: types.Message) -> None:
    button = types.InlineKeyboardButton(text="Проф. помощь", url="http://yasno.live/?ysclid=m6g5tdgprs390565986")
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.reply("Держи 😝", reply_markup=markup)

#запрос на ввод пользователя к gigaChat
@dp.message(F.text == "Хочу поддержку🙁")
async def cmd_mental_giga_help(message: types.Message, state: FSMContext) -> None:
    kb = [
        [
            types.KeyboardButton(text="Нужна помощь!"),
            types.KeyboardButton(text="Стоп")
        ],
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.reply(text="Что вас тревожит?", reply_markup=markup)
    await state.set_state(UserState.waiting_for_response)

#остановка состояния(выход)
@dp.message(UserState.waiting_for_response, F.text.casefold() == "стоп")
async def bot_stop(message: types.Message, state: FSMContext) -> None:
    markup = types.ReplyKeyboardMarkup(keyboard=kb_start, resize_keyboard=True)
    await message.reply(text="💫Поток сообщений остановлен💫\nЧтобы заново начать чат с помощником нажмите\nХочу поддержку🙁", reply_markup=markup)
    await state.clear()

#ожидание ответа пользователя и генерация запроса gigaChat
@dp.message(UserState.waiting_for_response)
async def bot_response(message: types.Message, state: FSMContext) -> None:
    user_text = message.text
    #bot_result = await MentalResponse.gigachat_response(user_text, giga)
    bot_result = "Запрос отправлен, но не тратиться API"
    print(bot_result)
    await message.reply(text=bot_result)

#отправлено фото
@dp.message(F.content_type.in_({'photo', 'voice'}))
async def bot_photo(message: types.Message) -> None:
    await message.reply("Бот не умеет обрабатывать изображения и голосовые сообщения")


#если команды нет и не в состоянии
@dp.message()
async def uncorrect_message(message: types.Message, state: FSMContext) -> None:
    await message.reply(text="Такой команды нет, воспользуейтесь командой\n[Хочу поддержку🙁] чтобы начать чат с помощником")

#
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")