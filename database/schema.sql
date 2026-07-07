-- schema.sql
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount INTEGER,
    raw_text TEXT
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount INTEGER,
    category_name TEXT,
    raw_text TEXT
);

CREATE TABLE IF NOT EXISTS budget (
    sumary INTEGER
);

INSERT INTO budget(sumary) VALUES (500);

-- Создаем индексы для ускорения запросов
CREATE INDEX idx_expenses_create_date ON expenses(create_date);
CREATE INDEX idx_income_create_date ON income(create_date);
CREATE INDEX idx_expenses_category ON expenses(category_name);