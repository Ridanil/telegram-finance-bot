from aiogram import types
from contextlib import suppress
import asyncio



async def delete_message(message: types.Message, seconds: int = 0):
    await asyncio.sleep(seconds)
    with suppress():
        await message.delete()
