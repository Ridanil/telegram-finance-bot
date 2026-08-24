import aiohttp

from telegram_bot.handlers.handlerQR import fetch_check_from_fns, format_processed_response
from telegram_bot.keyboards import kb_client
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from aiogram import Dispatcher, F
from aiogram.types import Message
import asyncio
import logging
import db
import exceptions
import processing
import categories
from telegram_bot.handlers import messageControl
from ai.receipt_processor import GigaChatProcessor
import os # TODO: узнать про дублирование импортирования библиотек в разных модулях
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


# Хранилище: user_id -> qr_value
qr_storage = {} # TODO: более продвинутое использование хранилища

API_TOKEN = os.getenv("FNS_API_TOKEN")  # Токен доступа к API

list_of_category: list = ['еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное']

class States(StatesGroup):
    waiting_for_category = State()

processor = GigaChatProcessor()

async def handle_qr(message: Message):
    qr_value = message.web_app_data.data
    user_id = message.from_user.id
    qr_storage[user_id] = qr_value

    # Отправляем уведомление о начале обработки
    await message.answer("🔄 Обрабатываю QR-код, запрашиваю данные чека у ФНС...")

    if not API_TOKEN:
        await message.answer("❌ Ошибка конфигурации: не указан токен API. Обратитесь к администратору.")
        return

    # Отправляем запрос к API
    try:
        api_response = await fetch_check_from_fns(qr_value, API_TOKEN)

        if api_response.get('code') != 1:
            await message.answer(f"❌ Ошибка получения чека: {api_response.get('code')}")
            return


        # 2. Обрабатываем чек через LLM
        await message.answer("🧠 Анализирую чек с помощью AI...")

        processed_data = await processor.categorize_items(api_response.get('data', {}).get('json', {}).get('items', []))

        if not processed_data:
            await message.answer("❌ Не удалось обработать чек. Попробуйте другой QR-код.")
            return

        # 3. Форматируем и отправляем результат
        result_text = format_processed_response(processed_data)  # Создайте эту функцию
        await message.answer(result_text, parse_mode="Markdown")

        # 4. Сохраняем данные в БД (опционально)
        # await save_receipt_to_db(user_id, processed_data)

        logging.info(f"User {user_id}: Receipt processed successfully")

    except aiohttp.ClientError as e:
        logging.error(f"HTTP error: {e}")
        await message.answer("❌ Ошибка соединения с сервером проверки чеков. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await message.answer(f"❌ Произошла непредвиденная ошибка: {str(e)}")

async def pick_message_income(message: Message):
    """Ловит сообщения начинающиеся с + и обрабатывает их как 'приход'"""
    try:
        pre_income = processing.parsing(message.text)
        await processing.add_income(pre_income.amount, pre_income.message_text)
        await message.answer(f"Добавлено {pre_income.amount} {pre_income.message_text}")
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return

async def pick_all_msg(message: Message, state: FSMContext):
    try:
        pre_expense = processing.parsing(message.text)
        await state.update_data(comment=pre_expense.message_text, amount=pre_expense.amount, date=pre_expense.date)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    try:
        expense_1 = categories.get_category(pre_expense.message_text)
        await state.update_data(category=expense_1)
        user_data = await state.get_data()
        await processing.add_expense(user_data['amount'], user_data['category'], user_data['comment'], user_data['date'])
        answer_message = f"Добавлены траты {user_data['amount']} руб., на {user_data['comment']}.\n Осталось {await db.get_budget()} руб."
        msg = await message.answer(answer_message)
        await asyncio.create_task(messageControl.delete_message(msg, 5))
    except exceptions.NoSuchCategory as e:
        msg = await message.answer(str(e), reply_markup=kb_client)
        await state.set_state(States.waiting_for_category)
        await asyncio.create_task(messageControl.delete_message(msg, 10))

async def category_choice(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    user_data = await state.get_data()
    categories.update_categories_json(user_data['comment'], user_data['category'])
    await processing.add_expense(user_data['amount'], user_data['category'], user_data['comment'], user_data['date'])
    answer_message = f"Добавлены траты {user_data['amount']} руб., на {user_data['comment']}. \n Осталось {await db.get_budget()} руб."
    msg = await message.answer(answer_message)
    await asyncio.create_task(messageControl.delete_message(message, 5))
    await asyncio.create_task(messageControl.delete_message(msg, 5))
    await state.clear()

async def cancel_input_budget(message: Message, state: FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply("Ok")

def register_handler_input_data(dp: Dispatcher):
    dp.message.register(handle_qr, lambda msg: msg.web_app_data is not None)
    dp.message.register(pick_message_income, F.text.startswith("+"))
    dp.message.register(category_choice, States.waiting_for_category, F.text.in_(list_of_category))
    dp.message.register(cancel_input_budget, Command('cancel'))
    dp.message.register(pick_all_msg, F.text, lambda msg: msg.web_app_data is None)
