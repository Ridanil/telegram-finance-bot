import logging
import asyncio
from aiogram import Bot, Dispatcher
from telegram_bot.handlers import input_data, statistics, admin

import os
from dotenv import load_dotenv, find_dotenv
from middlewares import CheckUserId
logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
access_id = list(map(int, (os.getenv('ACCESS_ID')).split(",")))

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher()
dp.message.middleware(CheckUserId(access_id))

statistics.register_handler_statistics(dp)
admin.register_handler_admin(dp)
input_data.register_handler_input_data(dp)

async def main() -> None:
   await dp.start_polling(bot)


if __name__ == '__main__':
   asyncio.run(main())
