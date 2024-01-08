from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import Dispatcher
from aiogram.filters.command import Command


import db
import processing


class States(StatesGroup):
    waiting_for_budget = State()
    waiting_for_new_value = State()

# @dp.message(commands="add_budget")
async def add_budget(message: types.Message, state: FSMContext):
    """Устанавливает бюджет"""
    await message.answer("Установите бюджет")
    await state.set_state(States.waiting_for_budget)


# @dp.message(state=BudgetState.waiting_for_budget.state)
async def input_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    user_data = await state.get_data()
    db.update_budget(user_data['budget'])
    answer_message = f"Добавлен бюджет {user_data['budget']} руб."
    await message.answer(answer_message)
    await state.clear()


# @dp.message(state="*", commands=['отмена'])
async def cancel_input(message: types.Message, state: FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply("Ok")


# @dp.message(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = processing.return_last_expenses()
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
    processing.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)

async def change_expense(message: types.Message, state: FSMContext):
    """Изменяет одну запись о расходе (сумму) по её идентификатору"""
    async with state.update_data() as new_value_data:
        new_value_data["row_id"] = int(message.text[4:])
    await message.answer("Введите новое значение (сумму)")
    await state.set_state(States.waiting_for_new_value)


# @dp.message(state=ChangeState.waiting_for_new_value.state)
async def new_value(message: types.Message, state: FSMContext):
    async with state.update_data() as new_value_data:
        new_value_data['new_amount'] = int(message.text)
    processing.change_expense(new_value_data['row_id'], new_value_data['new_amount'])
    answer_message = f"Изменения внесены."
    await message.answer(answer_message)
    await state.clear()


def register_handler_admin(dp: Dispatcher):
    dp.message.register(add_budget, Command('add_budget'))
    dp.message.register(input_budget, States.waiting_for_budget)
    dp.message.register(cancel_input, Command('cancel'))
    dp.message.register(list_expenses, Command('expenses'))
    dp.message.register(del_expense, lambda message: message.text.startswith('/del'))
    dp.message.register(change_expense, lambda message: message.text.startswith('/chg'))
    dp.message.register(new_value, States.waiting_for_new_value)