import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegram_bot.handlers import input_data, statistics, admin

import os
from dotenv import load_dotenv, find_dotenv
from middlewares import AccessMiddleware
logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
access_id = list(map(int, (os.getenv('ACCESS_ID')).split(",")))

bot = Bot(token=os.getenv('API_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(access_id))

statistics.register_handler_statistics(dp)
admin.register_handler_admin(dp)
input_data.register_handler_input_data(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
