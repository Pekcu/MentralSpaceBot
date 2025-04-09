# GigaChat
from aiohttp.web_fileresponse import content_type
from langchain.chains.question_answering.map_reduce_prompt import messages
from langchain.schema import HumanMessage, SystemMessage
from langchain_gigachat.chat_models.gigachat import GigaChat

# Aiogram libs
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command

# Other libs
import asyncio
import json
import logging
import sys
import random

# Библиотеки модуля шуток и модуля поддержки
from notProject import JokeGenerator
from mentalResponse import MentalResponse

# Получаем ключ телеграм и сбер API
with open("api_config.json") as api_config:
    config = json.load(api_config)
    token = config["bot_api_token"]
    sber_aut = config["sber_aut"]

# Модуль мотивации, загрузка категорий
with open("motivation_techniques.json", encoding="utf-8") as f:
    data = json.load(f)

quotes = [item for item in data if item["category"] == "цитата"]
techniques = [item for item in data if item["category"] == "техника"]
story = [item for item in data if item["category"] == "история"]
article = [item for item in data if item["category"] == "статья"]


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

# Начальный кнопки для события (start)
kb_start = [
        [
           types.KeyboardButton(text="🤗Хочу поддержку🤗")
        ],
        [
            types.KeyboardButton(text="✨Вдохновение✨")
        ],
        [
            types.KeyboardButton(text="😂Хочу анекдот😂"),
            types.KeyboardButton(text="🆘 Нужна помощь 🆘")
        ],
    ]

class UserState(StatesGroup):
    waiting_for_response = State()

# Базовый хэндлер при старте бота
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    markup = types.ReplyKeyboardMarkup(keyboard=kb_start, resize_keyboard=True)
    await message.answer("Привет, я бот, пока умею только анекдот, хочешь анекдот?",reply_markup=markup)

# Хэндлер показывает возможности бота
@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer("не сейчас")

# Хэндлер для генерации анекдота
@dp.message(F.text == "😂Хочу анекдот😂")
async def cmd_joke(message: types.Message) -> None:
    ranom_joke = await JokeGenerator.randomJoke()
    await message.answer(str(ranom_joke))

# Переход на сайт к проф-помощи через ответ.
@dp.message(F.text == "🆘 Нужна помощь 🆘")
async def cmd_mental_help(message: types.Message) -> None:
    button = types.InlineKeyboardButton(text="Проф. помощь", url="http://yasno.live/?ysclid=m6g5tdgprs390565986")
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.reply("Держи 😝", reply_markup=markup)

# Получение случайного вдохновения из категории кнопок
@dp.message(F.text == "✨Вдохновение✨")
async def cmd_inspiration(message: types.Message) -> None:
    kb = [
        [types.InlineKeyboardButton(text="🧠 Техники", callback_data="button_tech")],
        [types.InlineKeyboardButton(text="💬 Цитаты", callback_data="button_quote")],
        [types.InlineKeyboardButton(text="📖 Истории", callback_data="button_story")],
        [types.InlineKeyboardButton(text="📝 Статьи", callback_data="button_article")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("*Выберите одну из категорий, чтобы получить полезную информацию:*", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

# Обработчики событий callback_data из встроенной клавиатуры
@dp.callback_query(F.data == 'button_tech')
async def process_callback_button_tech(call: types.CallbackQuery) -> None:
    await call.answer()
    random_tech = random.randint(0, len(techniques) - 1)
    await call.message.answer(text=f"*{techniques[random_tech]['title']}*\n\n{techniques[random_tech]['text']}", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == 'button_quote')
async def process_callback_button_quote(call: types.CallbackQuery) -> None:
    await call.answer()
    random_quote = random.randint(0, len(quotes) - 1)
    await call.message.answer(text=quotes[random_quote]['text'], parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == 'button_story')
async def process_callback_button_story(call: types.CallbackQuery) -> None:
    await call.answer()
    random_story = random.randint(0, len(story) - 1)
    await call.message.answer(text=f"*{story[random_story]['title']}*\n{story[random_story]['text']}", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == 'button_article')
async def process_callback_button_article(call: types.CallbackQuery) -> None:
    await call.answer()
    random_article = random.randint(0, len(article) - 1)
    button = types.InlineKeyboardButton(text=f"{article[random_article]["title"]}", url=article[random_article]["text"])
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
    await call.message.answer("Прочитай, поможет:", reply_markup=markup)

# Запрос на ввод пользователя к gigaChat
@dp.message(F.text == "🤗Хочу поддержку🤗")
async def cmd_mental_giga_help(message: types.Message, state: FSMContext) -> None:
    kb = [
        [
            types.KeyboardButton(text="🆘 Нужна помощь 🆘"),
            types.KeyboardButton(text="Стоп")
        ],
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.reply(text="Что вас тревожит?", reply_markup=markup)
    await state.set_state(UserState.waiting_for_response)

# Остановка состояния(выход)
@dp.message(UserState.waiting_for_response, F.text.casefold() == "стоп")
async def bot_stop(message: types.Message, state: FSMContext) -> None:
    markup = types.ReplyKeyboardMarkup(keyboard=kb_start, resize_keyboard=True)
    await message.reply(text="💫Поток сообщений остановлен💫\n\nЧтобы заново начать чат с помощником нажмите\n\n🤗Хочу поддержку🤗", reply_markup=markup)
    await state.clear()

# Ожидание ответа пользователя и генерация запроса gigaChat
@dp.message(UserState.waiting_for_response)
async def bot_response(message: types.Message, state: FSMContext) -> None:
    user_text = message.text
    #bot_result = await MentalResponse.gigachat_response(user_text, giga)
    bot_result = "Запрос отправлен, но не тратиться API"
    print(bot_result)
    await message.reply(text=bot_result)

# Отправлено фото или голсовое
@dp.message(F.content_type.in_({'photo', 'voice'}))
async def bot_photo(message: types.Message) -> None:
    await message.reply("Бот не умеет обрабатывать изображения и голосовые сообщения")


# Команды нет и не в состоянии
@dp.message()
async def uncorrect_message(message: types.Message, state: FSMContext) -> None:
    await message.reply(text="Такой команды нет.\nВоспользуейтесь командой [🤗Хочу поддержку🤗] чтобы начать чат с помощником")

# Запуск бота с использованием асинхронного подхода и обработчика событий
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")