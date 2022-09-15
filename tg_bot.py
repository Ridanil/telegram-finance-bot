import logging
import processing
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

API_TOKEN = ("5059467386:AAGO8JytVDXBq-03W3YaFkvTNvKFqM6BpJ0")
ACCESS_ID = ("736489732")


bot = Bot(token = API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands = ['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler()
async def pick_all_msg(message: types.Message):
	expense = processing.add_expens(message.text)
	answer_message = f"Добавлены траты {expense.amount} на {expense.category_name}"
	await message.answer(answer_message)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
