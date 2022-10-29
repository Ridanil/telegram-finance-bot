import os
from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect("db/createdb.db")
cur = conn.cursor()
	
def insert(table: str, column_values: Dict):
	columns = ', '.join(column_values.keys())
	values = [tuple(column_values.values())]
	placeholders = ', '.join('?'* len(column_values.keys()))
	cur.executemany(
		f"INSERT INTO {table}"
		f"({columns})"
		f"VALUES ({placeholders})",
		values)
	conn.commit()


cur.execute("SELECT amount, category_name, raw_text FROM expenses WHERE category_name = 'еда'")
asd = cur.fetchall()
conn.commit()
for i in asd:
    print(i)