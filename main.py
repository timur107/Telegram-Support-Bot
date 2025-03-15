from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import sqlite3
import asyncio
from config import *


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подключение к базе данных
conn = sqlite3.connect("support_requests.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    department TEXT,
                    message TEXT)''')
conn.commit()

# Часто задаваемые вопросы
FAQ = {
    "Как оформить заказ?": 'Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку "Добавить в корзину", затем перейдите в корзину и следуйте инструкциям для завершения покупки.',
    "Как узнать статус моего заказа?": 'Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел "Мои заказы". Там будет указан текущий статус вашего заказа.',
    'Как отменить заказ?': 'Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.',
    'Что делать, если товар пришел поврежденным?': 'При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.',
    'Как связаться с вашей технической поддержкой?': 'Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.',
    'Как узнать информацию о доставке?': 'Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.'
}

# Клавиатура для быстрого выбора
faq_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=question)] for question in FAQ.keys()] +
             [[KeyboardButton(text="Связаться с поддержкой")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer('Здравствуйте! Я бот технической поддержки интернет-магазина "Продаем все на свете". Выберите вопрос или свяжитесь с поддержкой.',
                         reply_markup=faq_keyboard)

@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if text in FAQ:
        await message.answer(FAQ[text])
    elif text == "Связаться с поддержкой" or "связаться с поддержкой":
        await message.answer("Опишите вашу проблему, и я передам ее специалистам.")
    else:
        user_id = message.from_user.id
        text = message.text.lower()

        if any(keyword in text for keyword in ["оплата", "программа", "программист", "сайт", "сайт не работает"]):
            department = "Программисты"
        else:
            department = "Продаж"

        cursor.execute("INSERT INTO requests (user_id, department, message) VALUES (?, ?, ?)", (user_id, department, text))
        conn.commit()

        await message.answer(f"Ваш запрос передан в отдел: {department}. Мы свяжемся с вами в ближайшее время.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())