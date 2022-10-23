from aiogram.types import ReplyKeyboardMarkup, KeyboardButtonPollType, ReplyKeyboardRemove

b1 = KeyboardButtonPollType("разное")

kb_client = ReplyKeyboardMarkup()

kb_client.add(b1)