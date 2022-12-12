from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram import Dispatcher


import db


class BudgetState(StatesGroup):
    waiting_for_budget = State()


# @dp.message_handler(commands="add_budget")
async def add_budget(message: types.Message, state: FSMContext):
    """Устанавливает бюджет"""
    await message.answer("Установите бюджет")
    await state.set_state(BudgetState.waiting_for_budget.state)


# @dp.message_handler(state=BudgetState.waiting_for_budget.state)
async def input_budget(message: types.Message, state: FSMContext):
    async with state.proxy() as budget_data:
        budget_data['budget'] = message.text
    db.update_budget(budget_data['budget'])
    answer_message = f"Добавлен бюджет {budget_data['budget']} руб."
    await message.answer(answer_message)
    await state.finish()


#@dp.message_handler(state="*", commands=['отмена'])
async def cancel_input(message: types.Message, state=FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Ok")


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(add_budget, commands='add_budget')
    dp.register_message_handler(input_budget, state=BudgetState.waiting_for_budget.state)
    dp.register_message_handler(cancel_input, state='*', commands='cancel')
