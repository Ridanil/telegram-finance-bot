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
        "create_date": _get_now_formated_datetime(),
        "amount": amount,
        "category_name": category,
        "raw_text": expense
        })
    db.insert_budget(db.get_budget() - amount)
    return Expense(id=None, amount=amount, category_name=category) # TODO для чего она это возвращает???


def add_income(amount: int, message_text: str):
    """Добавляет новый приход(ЗП, пенсия и т.д)"""
    #add_in_to_gs = quikstart.add_into_gs(amount, category)
    insert_in_db = db.insert("income", {
        "create_date": _get_now_formated_datetime(),
        "amount": amount,
        "raw_text": message_text
        })
    pass


def parsing(raw_message: str) -> Message:
    parsed_msg = re.match(r"([\d ]+) (.*)", raw_message)
    if not parsed_msg or not parsed_msg.group(0) \
        or not parsed_msg.group(1) or not parsed_msg.group(2):
        raise exceptions.NotCorrectMessage("Неверно введен расход. Надо вот так:"
                                            " Сначала цифры потом буквы")
    amount = int(parsed_msg.group(1))
    message_text = str(parsed_msg.group(2)).strip()
    return Message(amount=amount, message_text=message_text)


def get_today_statistics() -> str:
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    cursor.execute("select sum(amount)"
                   "from expenses where date(create_date)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]
    # cursor.execute("select sum(amount) "
    #                "from expense where date(created)=date('now', 'localtime') "
    #                "and category_codename in (select codename "
    #                "from category where is_base_expense=true)")
    # result = cursor.fetchone()
    # base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы сегодня:\n"
            f"всего — {all_today_expenses} руб.\n")
            # f"базовые — {base_today_expenses} руб. из {_get_budget_limit()} руб.\n\n"
            # f"За текущий месяц: /month")
    

def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учетом временной зоны"""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def _get_now_formated_datetime() -> str:
    """Возвращает сегодняшнюю дату время строкой для БД"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")
