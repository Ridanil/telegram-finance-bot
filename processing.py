from typing import NamedTuple, Optional, List
import datetime
import pytz
import re

import quikstart
import db
import categories
import exceptions


class Message(NamedTuple):
    "Распаршенное сообщение"
    amount: int
    message_text: str

class Expense(NamedTuple):
    "Структура расхода"
    id: Optional[int]
    amount: int
    category_name: str

def add_expense(amount: int, category: str, expense: str):
    add_in_to_gs = quikstart.add_into_gs(amount, category)
    insert_in_db = db.insert("expenses", {
        "crete_date": _get_now_formated_datetime(),
        "amount": amount,
        "category_name": category,
        "raw_text": expense
        })
    return Expense(id=None, amount=amount, category_name=category) # TODO для чего она это возвращает???


def parsing(raw_message: str) -> Message:
    parsed_msg = re.match(r"([\d ]+) (.*)", raw_message)
    if not parsed_msg or not parsed_msg.group(0) \
        or not parsed_msg.group(1) or not parsed_msg.group(2):
        raise exceptions.NotCorrectMessage("Неверно введен расход. Надо вот так:"
                                            " Сначала сумма потом расход")
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
