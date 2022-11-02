import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import exceptions
import processing
import categories
import db
from keyboards import kb_client, kb_client_statistic

logging.basicConfig(level=logging.INFO)

API_TOKEN = ("5059467386:AAGO8JytVDXBq-03W3YaFkvTNvKFqM6BpJ0")
ACCESS_ID = ("736489732")


bot = Bot(token = API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

list_of_category = categories.get_list_of_category()


class Expenses_State(StatesGroup):
    waiting_for_category = State()

class Budget_State(StatesGroup):
    waiting_for_budget = State()

class Statistic_State(StatesGroup):
    wait_category_statistic = State()

@dp.message_handler(lambda message: message.text.startswith("+"))
async def pick_message_income(message: types.Message):
    pre_income = processing.parsing(message.text)
    processing.add_income(pre_income.amount, pre_income.message_text)
    await message.answer(f"Добавлено {pre_income.amount} {pre_income.message_text} it")



@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = processing.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['budget'])
async def budget_viewing(message: types.Message):
    """Отправляет состояние бюджета"""
    answer_message = db.get_budget()
    await message.answer(answer_message)


@dp.message_handler(commands="add_budget")
async def add_budget(message: types.Message, state: FSMContext):
    await message.answer("Установите бюджет")        
    await state.set_state(Budget_State.waiting_for_budget.state)   

@dp.message_handler(state=Budget_State.waiting_for_budget.state)
async def set_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as budget_data:
        budget_data['budget'] = message.text
    db.update_budget(budget_data['budget'])
    answer_message = f"Добавлен бюджет {budget_data['budget']} руб."
    await message.answer(answer_message)
    await state.finish()

@dp.message_handler(commands="month")
async def month_statistic(message: types.Message, state: FSMContext):
    await message.answer("Какую категорию посмотрим?", reply_markup=kb_client_statistic)      
    await state.set_state(Statistic_State.wait_category_statistic.state)   

@dp.message_handler(state=Statistic_State.wait_category_statistic.state)
async def month_statistics(message: types.Message, state: FSMContext):
    async with state.proxy() as category:
        category['category'] = message.text
    month_statistic = processing.get_month_statistic(category['category'])
    await message.answer(month_statistic)
    await state.finish()


@dp.message_handler()
async def pick_all_msg(message: types.Message, state: FSMContext):
    try:
        pre_expense = processing.parsing(message.text)
        async with state.proxy() as data:
            data['comment'] = pre_expense.message_text
            data['amount'] = pre_expense.amount
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    try:
        expense_1 = categories.get_category(pre_expense.message_text)
        async with state.proxy() as data:
            data['category'] = expense_1
        processing.add_expense(data['amount'], data['category'], data['comment'])
        answer_message = f"Добавлены траты {data['amount']} руб., на {data['comment']}.\n Осталось {db.get_budget()}"
        await message.answer(answer_message)
    except exceptions.NoSuchCategory as e:
        await message.answer(str(e), reply_markup=kb_client)        
        await state.set_state(Expenses_State.waiting_for_category.state)  

@dp.message_handler(Text(equals=list_of_category, ignore_case=True), state=Expenses_State.waiting_for_category)
async def category_choice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text
    categories.update_categories_json(data['comment'], data['category'])
    processing.add_expense(data['amount'], data['category'], data['comment'])
    answer_message = f"Добавлены траты {data['amount']} руб., на {data['comment']}. \n Осталось {db.get_budget()}"
    await message.answer(answer_message)
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
