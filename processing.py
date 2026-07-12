# processing.py (обновленная версия)
from typing import NamedTuple, Optional
import datetime
import pytz
import re
import db
import exceptions

class Message(NamedTuple):
    amount: int
    message_text: str
    date: Optional[str]

class Expense(NamedTuple):
    id: Optional[int]
    amount: int
    category_name: Optional[str]
    raw_text: Optional[str]

class Earn(NamedTuple):
    amount: int
    category_name: str

async def add_expense(amount: int, category: str, expense: str, date: str) -> Expense:
    """Добавляет новый расход"""
    db.insert("expenses", {
        "create_date": _get_now_formated_datetime(date),
        "amount": amount,
        "category_name": category,
        "raw_text": expense
    })
    current_budget = await db.get_budget()
    db.update_budget( await db.get_budget() - amount)
    return Expense(id=None, amount=amount, category_name=category, raw_text=None)

def add_income(amount: int, message_text: str) -> None:
    """Добавляет новый приход"""
    db.insert("income", {
        "create_date": _get_now_formated_datetime(),
        "amount": amount,
        "raw_text": message_text
    })
    db.update_budget(db.get_budget() + amount)

def parsing(raw_message: str) -> Message:
    """Парсит входящее сообщение"""
    parsed_msg = re.match(r"\A\+?(\d+)(\D+)(\d{1,2}-\d{1,2})?", raw_message)
    if not parsed_msg or not parsed_msg.group(0) \
        or not parsed_msg.group(1) or not parsed_msg.group(2):
        raise exceptions.NotCorrectMessage("Неверно сообщение. Сначала цифры-(сколько) потом буквы-(на что)")
    
    amount = int(parsed_msg.group(1))
    message_text = str(parsed_msg.group(2)).strip()
    date = str(parsed_msg.group(3)) if parsed_msg.group(3) else None
    
    return Message(amount=amount, message_text=message_text, date=date)

def get_today_statistics() -> str:
    """Возвращает статистику расходов за сегодня"""
    result = db.execute_query(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE date(create_date) = CURRENT_DATE"
    )
    all_today_expenses = result[0][0] if result else 0
    
    if all_today_expenses == 0:
        return "Сегодня ещё нет расходов"
    
    return f"Расходы сегодня:\nвсего — {all_today_expenses} руб.\n"

def get_month_statistic(category: str) -> str:
    """Возвращает статистику расходов за месяц"""
    now = _get_now_datetime()
    today = int(f'{now.day:02d}')
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    
    result = db.execute_query(db.month_statistic_query, (first_day_of_month, category))
    all_month_expenses = result[0][0] if result and result[0] else 0
    
    if all_month_expenses == 0:
        return "В этом месяце ещё нет расходов"
    
    avg = db.get_average(today, first_day_of_month, category)
    return (f"Расходы в текущем месяце: \n"
            f"{category} — {all_month_expenses} руб.\n"
            f"Среднее {avg:.2f} руб.")

def get_earn_statistic():
    """Возвращает статистику прихода за месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    
    result = db.execute_query(db.month_earn_query, (first_day_of_month,))
    earn = [Earn(amount=res[0], category_name=res[1]) for res in result]
    return earn

def return_last_expenses():
    """Возвращает 10 последних записей"""
    result = db.execute_query(db.last_expenses_query)
    last_expenses = [Expense(id=row[0], amount=row[1],
                            raw_text=row[2], category_name=None) for row in result]
    return last_expenses

def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    result = db.execute_query(db.amount_and_category_query, (row_id,))
    if result:
        rows = result[0]
        date = str(rows[2])[8:10]
        # quikstart.add_into_gs(-abs(int(rows[0])), rows[1], int(date)) # Раскомментировать при необходимости
    db.delete("expenses", row_id)

def change_expense(row_id: int, new_value: int) -> None:
    """Изменяет запись расхода по его идентификатору"""
    result = db.execute_query(db.amount_and_category_query, (row_id,))
    if result:
        rows = result[0]
        date = str(rows[2])[8:10]
        # quikstart.add_into_gs(new_value-rows[0], rows[1], int(date)) # Раскомментировать при необходимости
    db.change("expenses", row_id, new_value)

def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учетом временной зоны"""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now

def _get_now_formated_datetime(specified_date=None) -> str:
    """Возвращает форматированную дату для БД"""
    if specified_date is None:
        date = _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date = (str(_get_now_datetime().year) + "-" +
                str(specified_date) + " " +
                _get_now_datetime().strftime("%H:%M:%S"))
    return date
