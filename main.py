import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

# Вставь свой токен от BotFather
TOKEN = "8707889831:AAEIozkS7gxBrDiRVKW4BVFP8luqlAwfnbQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Клавиатуры ---

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🎁 Сделать подарок", callback_data="make_gift")],
        [InlineKeyboardButton(text="👤 Я", callback_data="my_profile")],
        [InlineKeyboardButton(text="🔄 Начать сначала", callback_data="restart")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def stars_menu():
    # Список звезд: 15, 30, 45, 60, 75, 90, 105, 120
    prices = [15, 30, 45, 60, 75, 90, 105, 120]
    buttons = []
    # Создаем кнопки по 2 в ряд
    row = []
    for amount in prices:
        row.append(InlineKeyboardButton(text=f"⭐️ {amount}", callback_data=f"buy_{amount}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="restart")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Хендлеры ---

@dp.message(Command("start"))
@dp.callback_query(F.data == "restart")
async def cmd_start(message: types.Message | types.CallbackQuery):
    text = (
        "Привет, юный дружок! 👋\n\n"
        "Уверен, ты фанат Алиночки, но если ты по-настоящему преданный, "
        "ты можешь подарить ей немного звёздочек! ✨"
    )
    image = FSInputFile("IMG_0205.webp")
    
    if isinstance(message, types.Message):
        await message.answer_photo(photo=image, caption=text, reply_markup=main_menu())
    else:
        await message.message.answer_photo(photo=image, caption=text, reply_markup=main_menu())
        await message.answer()

@dp.callback_query(F.data == "make_gift")
async def choose_gift(callback: types.CallbackQuery):
    text = "Хорошо! Тогда выбери, сколько хочешь подарить Алиночке звёзд (Telegram Stars) 👇"
    image = FSInputFile("IMG_0219.jpeg")
    
    await callback.message.answer_photo(photo=image, caption=text, reply_markup=stars_menu())
    await callback.answer()

@dp.callback_query(F.data == "my_profile")
async def my_profile(callback: types.CallbackQuery):
    await callback.answer("Ты — самый верный фанат! ⭐", show_alert=True)

@dp.callback_query(F.data.startswith("buy_"))
async def create_invoice(callback: types.CallbackQuery):
    stars_count = int(callback.data.split("_")[1])
    
    # Для Telegram Stars provider_token должен быть ПУСТЫМ
    await callback.message.answer_invoice(
        title=f"Подарок для Алиночки",
        description=f"Донат в размере {stars_count} звёзд. Спасибо за поддержку!",
        payload=f"gift_{stars_count}_stars",
        currency="XTR",  # Код валюты для Telegram Stars
        prices=[LabeledPrice(label="Звёзды", amount=stars_count)],
        provider_token="" 
    )
    await callback.answer()

# Хендлер подтверждения платежа (нужен обязательно)
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# Хендлер успешной оплаты
@dp.message(F.successful_payment)
async def success_payment_handler(message: types.Message):
    await message.answer(f"Спасибо за твой подарок в {message.successful_payment.total_amount} звёзд! Алиночка счастлива! ❤️")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
