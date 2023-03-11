from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegram_bot.keyboards import kb_client_statistic
from telegram_bot.handlers import messageControl
import processing
import db
import os

import asyncio


bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)


class StatisticState(StatesGroup):
    wait_category_statistic = State()


#@dp.message_handler(commands=['start'])
async def say_hello(message: types.Message):
    """приветственное сообщение"""
    answer_message = "Бот для учета финансов. Все необходимые команды в пункте меню."
    msg = await message.answer(answer_message)
    asyncio.create_task(messageControl.delete_message(msg, 10))



#@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = processing.get_today_statistics()
    await message.answer(answer_message)


#@dp.message_handler(commands=['earn'])
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


#@dp.message_handler(commands=['budget'])
async def budget_viewing(message: types.Message):
    """Отправляет состояние бюджета"""
    answer_message = db.get_budget()
    await message.answer(answer_message)
    asyncio.create_task(messageControl.delete_message(answer_message, 8))


#@dp.message_handler(commands="month")
async def start_month_statistic(message: types.Message, state: FSMContext):
    await message.answer("Какую категорию посмотрим?", reply_markup=kb_client_statistic)
    await state.set_state(StatisticState.wait_category_statistic.state)


#@dp.message_handler(state=StatisticState.wait_category_statistic.state)
async def month_statistics(message: types.Message, state: FSMContext):
    async with state.proxy() as category:
        category['category'] = message.text
    await message.answer(processing.get_month_statistic(category['category']))
    await state.finish()


#@dp.message_handler(state="*", commands=['отмена'])
async def cancel_input_category(message: types.Message, state=FSMContext):
    """Прерывает ввод категории"""
    curent_state = await state.get_state()
    if curent_state is None:
        return
    await state.finish()
    await message.reply("Ok")

def register_handler_statistics(dp: Dispatcher):
    dp.register_message_handler(say_hello, commands=['start'])
    dp.register_message_handler(today_statistics, commands=['today'])
    dp.register_message_handler(month_earn, commands=['earn'])
    dp.register_message_handler(budget_viewing, commands=['budget'])
    dp.register_message_handler(start_month_statistic, commands="month")
    dp.register_message_handler(month_statistics, state=StatisticState.wait_category_statistic.state)
    dp.register_message_handler(cancel_input_category, state='*', commands='cancel')
