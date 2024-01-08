from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

class CheckUserId(BaseMiddleware):
    def __init__(self, access_id: list):
        self.access_id = access_id

    def get_user_id(self, user_id: int):
        if user_id in self.access_id:
            return True
        else:
            return False

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        result = self.get_user_id(user.id)
        if result:
            return await handler(event, data)
