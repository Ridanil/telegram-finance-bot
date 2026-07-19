# database.py
import os
import asyncpg
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Tuple, Optional
from asyncpg import Record
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Настройки подключения
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'budget_bot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создает пул соединений с БД"""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    **self.db_config,
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    timeout=30
                )
                logger.info("Database pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise
        return self.pool

    async def close(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Контекстный менеджер для получения соединения из пула"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                yield conn
            except Exception as e:
                logger.error(f"Database error: {e}")
                raise

    @asynccontextmanager
    async def get_cursor(self, commit: bool = True):
        """Контекстный менеджер для работы с транзакциями"""
        async with self.get_connection() as conn:
            # Используем транзакцию
            async with conn.transaction():
                try:
                    yield conn
                    if commit:
                        pass
                except Exception as e:
                    raise e

    async def insert(self, table: str, column_values: Dict[str, Any]) -> int:
        """Вставка данных и возврат ID"""
        columns = ', '.join(column_values.keys())
        placeholders = ', '.join([f'${i+1}' for i in range(len(column_values))])
        values = list(column_values.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        
        async with self.get_cursor() as conn:
            result = await conn.fetchrow(query, *values)
            return result['id'] if result else 0

    async def insert_many(self, table: str, column_values_list: List[Dict[str, Any]]):
        """Массовая вставка данных"""
        if not column_values_list:
            return
        
        columns = ', '.join(column_values_list[0].keys())
        placeholders = ', '.join([f'${i+1}' for i in range(len(column_values_list[0]))])
        
        async with self.get_cursor() as conn:
            for values in column_values_list:
                query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                await conn.execute(query, *values.values())

    async def get_budget(self) -> int:
        """Получение текущего бюджета"""
        async with self.get_connection() as conn:
            result = await conn.fetchval("SELECT sumary FROM budget LIMIT 1")
            return result if result else 0

    async def update_budget(self, value: int):
        """Обновление бюджета"""
        async with self.get_cursor() as conn:
            await conn.execute("UPDATE budget SET sumary = $1", value)

    async def get_average(self, today: int, first_day_of_month: str, category: str) -> Optional[float]:
        """Получение среднего значения расходов"""
        query = """SELECT COALESCE(AVG(amount), 0) FROM expenses 
                   WHERE date(create_date) >= $1 
                   AND category_name LIKE $2"""
        async with self.get_connection() as conn:
            result = await conn.fetchval(query, first_day_of_month, category)
            return float(result) if result is not None else None

    async def delete(self, table: str, row_id: int):
        """Удаление записи"""
        async with self.get_cursor() as conn:
            await conn.execute(f"DELETE FROM {table} WHERE id = $1", row_id)

    async def change(self, table: str, row_id: int, new_value: int):
        """Изменение суммы в записи"""
        async with self.get_cursor() as conn:
            await conn.execute(
                f"UPDATE {table} SET amount = $1 WHERE id = $2",
                new_value, row_id
            )

    async def execute_query(self, query: str, params: Tuple = ()) -> List[Record]:
        """Выполнение произвольного запроса"""
        async with self.get_connection() as conn:
            if params:
                return await conn.fetch(query, *params)
            return await conn.fetch(query)

    async def execute_query_dict(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Выполнение произвольного запроса с возвратом словарей"""
        async with self.get_connection() as conn:
            if params:
                rows = await conn.fetch(query, *params)
            else:
                rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def get_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Получение одной записи в виде словаря"""
        async with self.get_connection() as conn:
            if params:
                row = await conn.fetchrow(query, *params)
            else:
                row = await conn.fetchrow(query)
            return dict(row) if row else None

    # Дополнительные полезные методы
    async def table_exists(self, table_name: str) -> bool:
        """Проверка существования таблицы"""
        query = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = $1
        )"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, table_name)

    async def get_table_size(self, table_name: str) -> int:
        """Получение количества записей в таблице"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        async with self.get_connection() as conn:
            return await conn.fetchval(query)

# Создаем глобальный экземпляр
db = Database()
