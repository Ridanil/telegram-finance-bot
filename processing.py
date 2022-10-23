from typing import NamedTuple, Optional, List
import datetime
import pytz
import re
import quikstart

import db
import categories


class Message(NamedTuple):
    "Распаршенное сообщение"
    amount: int
    message_text: str

class Expense(NamedTuple):
    "Структура расхода"
    id: Optional[int]
    amount: int
    category_name: str

def add_expens(raw_message: str):
    parsed_message = parsing(raw_message)
    category = categories.get_category(parsed_message.message_text)
    add_in_to_gs = quikstart.add_into_gs(
        parsed_message.amount,
        category
        )
    insert_in_db = db.insert("expenses", {
        "crete_date": _get_now_formated_datetime(),
        "amount": parsed_message.amount,
        "category_name": category,
        "raw_text": parsed_message.message_text
        })
    return Expense(id=None, amount=parsed_message.amount, category_name=category)


def parsing(raw_message: str) -> Message:
    parsed_msg = re.match(r"([\d ]+) (.*)", raw_message)
    amount = int(parsed_msg.group(1))
    message_text = str(parsed_msg.group(2)).strip()
    return Message(amount=amount, message_text=message_text)

def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учетом временной зоны"""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def _get_now_formated_datetime() -> str:
    """Возвращает сегодняшнюю дату время строкой для БД"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")
