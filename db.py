from typing import Dict


import sqlite3

conn = sqlite3.connect("db/createdb.db")
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
	columns = ', '.join(column_values.keys())
	values = [tuple(column_values.values())]
	placeholders = ', '.join('?'* len(column_values.keys()))
	cursor.executemany(
		f"INSERT INTO {table}"
		f"({columns})"
		f"VALUES ({placeholders})",
		values)
	conn.commit()


def get_budget():
	cursor.execute(f"SELECT sumary FROM budget")
	budget = cursor.fetchone()
	conn.commit()
	return budget[0]


def get_averege(today, first_day_of_month, category):
	cursor.execute("""SELECT sum(amount)/? FROM expenses WHERE date(create_date) >= ?
					AND (category_name LIKE ?)""",(today, first_day_of_month, category))
	avg = cursor.fetchone()
	conn.commit()
	return avg[0]


def update_budget(values: int):
	cursor.execute(f"UPDATE budget SET sumary = {values}")
	conn.commit()


def get_cursor():
	return cursor


def delete(table: str, row_id: int) -> None:
	row_id = int(row_id)
	cursor.execute(f"delete from {table} where id={row_id}")
	conn.commit()


def change(table: str, row_id: int, new_value: int) -> None:
	row_id = int(row_id)
	new_value = int(new_value)
	cursor.execute(f"UPDATE {table} SET amount = {new_value} where id={row_id}")
	conn.commit()


month_statistic_query = """SELECT sum(amount) FROM expenses
						WHERE date(create_date) >= ?
						AND (category_name LIKE ?)"""


month_earn_query = """SELECT amount, raw_text FROM income
						WHERE date(create_date) >= ?"""


last_expenses_query = """SELECT id, amount, raw_text FROM expenses
						ORDER BY create_date DESC limit 10"""

amount_and_category_query = """SELECT amount, category_name, create_date FROM expenses WHERE id = ?"""
