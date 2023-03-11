from aiogram import types
from contextlib import suppress
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
import asyncio



async def delete_message(message: types.Message, seconds: int = 0):
    await asyncio.sleep(seconds)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()