from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

#b1 = KeyboardButton('разное')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_client.add('еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное')