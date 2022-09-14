from typing import NamedTuple, Optional, List
import datetime
import pytz
import re

class Message(NamedTuple):
    "Распаршенное сообщение"
    amount: int
    category_text: str

#def add_expens(raw_message: str)

def parsing(raw_message: str) -> Message:
    parsed_msg = re.match(r"([\d ]+) (.*)", raw_message)
    amount = parsed_msg.group(1)
    category_text = parsed_msg.group(2)
    return Message(amount=amount, category_text=category_text)
