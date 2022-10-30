import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import exceptions
import processing
import categories
from keyboards import kb_client

logging.basicConfig(level=logging.INFO)

API_TOKEN = ("5059467386:AAGO8JytVDXBq-03W3YaFkvTNvKFqM6BpJ0")
ACCESS_ID = ("736489732")


bot = Bot(token = API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

list_of_category = categories.get_list_of_category()


class Expenses_State(StatesGroup):
	waiting_for_category = State()


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = processing.get_today_statistics()
    await message.answer(answer_message)


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
        answer_message = f"Добавлены траты {data['amount']} руб., на {data['comment']}"
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
    answer_message = f"Добавлены траты {data['amount']} руб., на {data['comment']}"
    await message.answer(answer_message)
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
