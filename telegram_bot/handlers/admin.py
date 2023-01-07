from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram import Dispatcher


import db
import processing


class BudgetState(StatesGroup):
    waiting_for_budget = State()

class ChangeState(StatesGroup):
    waiting_for_new_value = State()

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


# @dp.message_handler(state="*", commands=['отмена'])
async def cancel_input(message: types.Message, state=FSMContext):
    """Прерывает ввод"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Ok")


# @dp.message_handler(commands=['expenses'])
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
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
        .join(last_expenses_rows)
    await message.answer(answer_message)

async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    processing.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)

async def change_expense(message: types.Message, state: FSMContext):
    """Изменяет одну запись о расходе по её идентификатору"""
    async with state.proxy() as new_value_data:
        new_value_data["row_id"] = int(message.text[4:])
    await message.answer("Введите новое значение")
    await state.set_state(ChangeState.waiting_for_new_value.state)


# @dp.message_handler(state=ChangeState.waiting_for_new_value.state)
async def new_value(message: types.Message, state: FSMContext):
    async with state.proxy() as new_value_data:
        new_value_data['new_amount'] = int(message.text)
    processing.change_expense(new_value_data['row_id'], new_value_data['new_amount'])
    answer_message = f"Изменения внесены."
    await message.answer(answer_message)
    await state.finish()


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(add_budget, commands='add_budget')
    dp.register_message_handler(input_budget, state=BudgetState.waiting_for_budget.state)
    dp.register_message_handler(cancel_input, state='*', commands='cancel')
    dp.register_message_handler(list_expenses, commands=['expenses'])
    dp.register_message_handler(del_expense, lambda message: message.text.startswith('/del'))
    dp.register_message_handler(change_expense, lambda message: message.text.startswith('/chg'))
    dp.register_message_handler(new_value, state=ChangeState.waiting_for_new_value.state)