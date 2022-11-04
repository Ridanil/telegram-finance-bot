import os
from typing import Dict, List, Tuple

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
	cursor.execute(f"SELECT sum FROM budget")
	budget = cursor.fetchone()
	conn.commit()
	return  budget[0]

def get_averege(today, first_day_of_month, category):
	cursor.execute("""SELECT sum(amount)/? FROM expenses WHERE date(create_date) >= ?
                        AND (category_name LIKE ?)""",(today, first_day_of_month, category))
	avg = cursor.fetchone()
	conn.commit()
	return avg[0]


def update_budget(values: int):
	cursor.execute(f"UPDATE budget SET sum = {values}")
	conn.commit()

def get_cursor():
	return cursor

month_statistic_query= """SELECT sum(amount) FROM expenses
	                    WHERE date(create_date) >= ?
                        AND (category_name LIKE ?)"""