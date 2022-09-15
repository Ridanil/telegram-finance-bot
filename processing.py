from typing import NamedTuple, Optional, List
import datetime
import pytz
import re
import quikstart

class Message(NamedTuple):
    "Распаршенное сообщение"
    amount: int
    category_text: str

class Expense(NamedTuple):
    "Структура расхода"
    id: Optional[int]
    amount: int
    category_name: str

def add_expens(raw_message: str):
	parsed_message = parsing(raw_message)
	add_in_to_gs = quikstart.add_into_gs(parsed_message.amount, parsed_message.category_text)
	return Expense(id=None, amount=parsed_message.amount, category_name=parsed_message.category_text)

def parsing(raw_message: str) -> Message:
    parsed_msg = re.match(r"([\d ]+) (.*)", raw_message)
    amount = int(parsed_msg.group(1))
    category_text = str(parsed_msg.group(2)).strip()
    return Message(amount=amount, category_text=category_text)
