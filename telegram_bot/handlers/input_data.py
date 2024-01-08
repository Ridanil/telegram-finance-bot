from telegram_bot.keyboards import kb_client
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from aiogram import Dispatcher, F
from aiogram.types import Message
import asyncio

import db
import exceptions
import processing
import categories
from telegram_bot.handlers import messageControl


list_of_category = ['еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное']


class States(StatesGroup):
    waiting_for_category = State()


#@dp.message(lambda message: message.text.startswith("+"))
async def pick_message_income(message: Message):
    """Ловит сообщения начинающиеся с + и обрабатывает их как 'приход'"""
    try:
        pre_income = processing.parsing(message.text)
        processing.add_income(pre_income.amount, pre_income.message_text)
        await message.answer(f"Добавлено {pre_income.amount} {pre_income.message_text}")
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return


#@dp.message()
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
        processing.add_expense(user_data['amount'], user_data['category'], user_data['comment'], user_data['date'])
        answer_message = f"Добавлены траты {user_data['amount']} руб., на {user_data['comment']}.\n Осталось {db.get_budget()}"
        msg = await message.answer(answer_message)
        await asyncio.create_task(messageControl.delete_message(msg, 5))
    except exceptions.NoSuchCategory as e:
        msg = await message.answer(str(e), reply_markup=kb_client)
        await state.set_state(States.waiting_for_category)
        await asyncio.create_task(messageControl.delete_message(msg, 10))


#@dp.message(States.waiting_for_category, F.text.in_(list_of_category))
async def category_choice(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    user_data = await state.get_data()
    categories.update_categories_json(user_data['comment'], user_data['category'])
    processing.add_expense(user_data['amount'], user_data['category'], user_data['comment'], user_data['date'])
    answer_message = f"Добавлены траты {user_data['amount']} руб., на {user_data['comment']}. \n Осталось {db.get_budget()}"
    msg = await message.answer(answer_message)
    await asyncio.create_task(messageControl.delete_message(message, 5))
    await asyncio.create_task(messageControl.delete_message(msg, 5))
    await state.clear()


# @dp.message(state="*", commands=['отмена'])
async def cancel_input_budget(message: Message, state: FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply("Ok")


def register_handler_input_data(dp: Dispatcher):
    dp.message.register(pick_message_income, F.text.startswith("+"))
    dp.message.register(category_choice, States.waiting_for_category, F.text.in_(list_of_category))
    dp.message.register(cancel_input_budget, Command('cancel'))
    dp.message.register(pick_all_msg)
