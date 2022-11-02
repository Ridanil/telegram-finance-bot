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

def update_budget(values: int):
	cursor.execute(f"UPDATE budget SET sum = {values}")
	conn.commit()

def get_cursor():
	return cursor

