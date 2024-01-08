from aiogram import Dispatcher, Bot, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from telegram_bot.keyboards import kb_client_statistic
from telegram_bot.handlers import messageControl
import processing
import db
import os

import asyncio


bot = Bot(token=os.getenv('API_TOKEN'))
#dp = Dispatcher()


class States(StatesGroup):
    wait_category_statistic = State()


#@dp.message(commands=['start'])
async def say_hello(message: types.Message):
    """приветственное сообщение"""
    answer_message = "Бот для учета финансов. Все необходимые команды в пункте меню."
    msg = await message.answer(answer_message)
    await asyncio.create_task(messageControl.delete_message(msg, 10))



#@dp.message(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = processing.get_today_statistics()
    await message.answer(answer_message)


#@dp.message(commands=['earn'])
async def month_earn(message: types.Message):
    last_expenses = processing.get_earn_statistic()
    if not last_expenses:
        await message.answer("Доходов ещё нет")
        return
    last_expenses_rows = [
        f"{expense.amount} руб. {expense.category_name}"
        for expense in last_expenses]
    answer_message = "Последние сохранённые плюсы:\n\n* " + "\n\n* " \
        .join(last_expenses_rows)
    await message.answer(answer_message)


#@dp.message(commands=['budget'])
async def budget_viewing(message: types.Message):
    """Отправляет состояние бюджета"""
    answer_message = db.get_budget()
    msg = await message.answer(str(answer_message))
    await asyncio.create_task(messageControl.delete_message(msg, 8))
    await asyncio.create_task(messageControl.delete_message(message, 3))


#@dp.message(commands="month")
async def start_month_statistic(message: types.Message, state: FSMContext):
    await message.answer("Какую категорию посмотрим?", reply_markup=kb_client_statistic)
    await state.set_state(States.wait_category_statistic)


#@dp.message(state=StatisticState.wait_category_statistic.state)
async def month_statistics(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    user_data = await state.get_data()
    await message.answer(processing.get_month_statistic(user_data['category']))
    await state.clear()


#@dp.messagedp.message.register(state="*", commands=['отмена'])
async def cancel_input_category(message: types.Message, state: FSMContext):
    """Прерывает ввод категории"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply("Ok")

def register_handler_statistics(dp: Dispatcher):
    dp.message.register(say_hello, Command('start'))
    dp.message.register(today_statistics, Command('today'))
    dp.message.register(month_earn, Command('earn'))
    dp.message.register(budget_viewing, Command('budget'))
    dp.message.register(start_month_statistic, Command("month"))
    dp.message.register(month_statistics, States.wait_category_statistic)
    dp.message.register(cancel_input_category, Command('cancel'))
