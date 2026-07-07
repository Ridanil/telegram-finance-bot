# migrate_data.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect("db/createdb.db")
    sqlite_cursor = sqlite_conn.cursor()
    
    # Подключение к PostgreSQL
    pg_conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'budget_bot'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    pg_cursor = pg_conn.cursor()
    
    try:
        # Миграция income
        print("Миграция income...")
        sqlite_cursor.execute("SELECT create_date, amount, raw_text FROM income")
        income_data = sqlite_cursor.fetchall()
        if income_data:
            execute_values(pg_cursor,
                "INSERT INTO income (create_date, amount, raw_text) VALUES %s",
                income_data
            )
        
        # Миграция expenses
        print("Миграция expenses...")
        sqlite_cursor.execute("SELECT create_date, amount, category_name, raw_text FROM expenses")
        expenses_data = sqlite_cursor.fetchall()
        if expenses_data:
            execute_values(pg_cursor,
                "INSERT INTO expenses (create_date, amount, category_name, raw_text) VALUES %s",
                expenses_data
            )
        
        # Миграция budget
        print("Миграция budget...")
        sqlite_cursor.execute("SELECT sumary FROM budget")
        budget_data = sqlite_cursor.fetchone()
        if budget_data:
            pg_cursor.execute("INSERT INTO budget (sumary) VALUES (%s)", (budget_data[0],))
        
        pg_conn.commit()
        print("Миграция успешно завершена!")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"Ошибка при миграции: {e}")
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_data()
