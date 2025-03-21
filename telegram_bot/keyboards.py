from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardMarkup

kb=[
        [types.KeyboardButton(text='еда') ],
        [types.KeyboardButton(text='кафе')],
        [types.KeyboardButton(text='алкоголь')],
        [types.KeyboardButton(text='сладкое')],
        [types.KeyboardButton(text='бензин')],
        [types.KeyboardButton(text='бытовая химия')],
        [types.KeyboardButton(text='разное')]
    ]

kb_client = ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите категорию")

kb_client_statistic = ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=False,
    input_field_placeholder="Выберите категорию")


# kb_client.add('еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное')

# kb_client_statistic.add('еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное')

