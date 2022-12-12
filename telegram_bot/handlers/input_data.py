from telegram_bot.keyboards import kb_client
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher


import db
import exceptions
import processing
import categories


list_of_category = categories.get_list_of_category()


class ExpensesState(StatesGroup):
    waiting_for_category = State()


#@dp.message_handler(lambda message: message.text.startswith("+"))
async def pick_message_income(message: types.Message):
    """Ловит сообщения начинающиеся с + и обрабатывает их как 'приход'"""
    try:
        pre_income = processing.parsing(message.text)
        processing.add_income(pre_income.amount, pre_income.message_text)
        await message.answer(f"Добавлено {pre_income.amount} {pre_income.message_text}")
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return


#@dp.message_handler()
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
        await state.set_state(ExpensesState.waiting_for_category.state)


# @dp.message_handler(Text(equals=list_of_category, ignore_case=True), state=ExpensesState.waiting_for_category)
async def category_choice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text
    categories.update_categories_json(data['comment'], data['category'])
    processing.add_expense(data['amount'], data['category'], data['comment'])
    answer_message = f"Добавлены траты {data['amount']} руб., на {data['comment']}. \n Осталось {db.get_budget()}"
    await message.answer(answer_message)
    await state.finish()


# @dp.message_handler(state="*", commands=['отмена'])
async def cancel_input_budget(message: types.Message, state=FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Ok")


def register_handler_input_data(dp: Dispatcher):
    dp.register_message_handler(pick_message_income, lambda message: message.text.startswith("+"))
    dp.register_message_handler(pick_all_msg)
    dp.register_message_handler(category_choice, Text(equals=list_of_category,
                                                      ignore_case=True),
                                state=ExpensesState.waiting_for_category)
    dp.register_message_handler(cancel_input_budget, state='*', commands='cancel')
