# db.py (новая версия)
from typing import Dict, Any, List, Optional
from database import db

def insert(table: str, column_values: Dict[str, Any]):
    """Вставляет данные в таблицу"""
    db.insert(table, column_values)

def get_budget() -> int:
    """Возвращает текущий бюджет"""
    return db.get_budget()

def get_average(today: int, first_day_of_month: str, category: str) -> float:
    """Возвращает среднее значение расходов"""
    return db.get_average(today, first_day_of_month, category)

def update_budget(value: int):
    """Обновляет бюджет"""
    db.update_budget(value)

def delete(table: str, row_id: int):
    """Удаляет запись"""
    db.delete(table, row_id)

def change(table: str, row_id: int, new_value: int):
    """Изменяет сумму в записи"""
    db.change(table, row_id, new_value)

def get_cursor():
    """Возвращает курсор - для обратной совместимости"""
    db.connect()
    return db.connection.cursor()

# SQL запросы
month_statistic_query = """SELECT COALESCE(SUM(amount), 0) FROM expenses
                        WHERE date(create_date) >= %s
                        AND category_name LIKE %s"""

month_earn_query = """SELECT amount, raw_text FROM income
                    WHERE date(create_date) >= %s"""

last_expenses_query = """SELECT id, amount, raw_text FROM expenses
                        ORDER BY create_date DESC LIMIT 10"""

amount_and_category_query = """SELECT amount, category_name, create_date 
                            FROM expenses WHERE id = %s"""
