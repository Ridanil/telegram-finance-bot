from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from dotenv import load_dotenv

import os
import db
import processing

load_dotenv()

VERCEL_URL = os.getenv("VERCEL_URL")  # без слеша в конце

class States(StatesGroup):
    waiting_for_budget = State()
    waiting_for_new_value = State()


async def start(message: types.Message):
    btn = KeyboardButton(text="📷 Сканировать QR", web_app=WebAppInfo(url=VERCEL_URL))
    keyboard = ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)
    await message.answer("Нажми кнопку и наведи камеру на QR-код чека", reply_markup=keyboard)

async def add_budget(message: types.Message, state: FSMContext):
    """Устанавливает бюджет"""
    await message.answer("Установите бюджет")
    await state.set_state(States.waiting_for_budget)

async def input_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    user_data = await state.get_data()
    await db.update_budget(user_data['budget'])
    answer_message = f"Добавлен бюджет {user_data['budget']} руб."
    await message.answer(answer_message)
    await state.clear()

async def cancel_input(message: types.Message, state: FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply("Ok")

async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = await processing.return_last_expenses()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return
    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.raw_text} — нажми "
        f"/del{expense.id} для удаления, /chg{expense.id} для изменения"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n* "\
        .join(last_expenses_rows)
    await message.answer(answer_message)

async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    await processing.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)

async def change_expense(message: types.Message, state: FSMContext):
    """Изменяет одну запись о расходе (сумму) по её идентификатору"""
    await state.update_data(row_id = int(message.text[4:]))
    #data["row_id"] = int(message.text[4:])
    await message.answer("Введите новое значение (сумму)")
    await state.set_state(States.waiting_for_new_value)

async def new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Получаем сохраненные данные
    row_id = data.get('row_id')
    new_amount = int(message.text)
    await processing.change_expense(row_id, new_amount)
    await message.answer("Изменения внесены.")
    await state.clear()


def register_handler_admin(dp: Dispatcher):
    dp.message.register(start, Command("start"))
    dp.message.register(add_budget, Command('add_budget'))
    dp.message.register(input_budget, States.waiting_for_budget)
    dp.message.register(cancel_input, Command('cancel'))
    dp.message.register(list_expenses, Command('expenses'))
    dp.message.register(del_expense, F.text, lambda msg: msg.text.startswith('/del'))
    dp.message.register(change_expense, F.text, lambda msg: msg.text.startswith('/chg'))
    dp.message.register(new_value, States.waiting_for_new_value)