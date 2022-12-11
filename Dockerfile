FROM python:3.9

WORKDIR /home


RUN pip install -U pip aiogram pytz google-api-python-client python-dotenv && apt-get update && apt-get install sqlite3

COPY db/createdb.db ./db/
COPY google_sheets/*.py ./google_sheets/
COPY google_sheets/*.json ./google_sheets/
COPY telegram_bot/handlers/*.py ./telegram_bot/handlers/
COPY telegram_bot/*.py ./telegram_bot/
COPY createdb.sql ./
COPY *.py ./
COPY *.json ./
COPY .env ./


ENTRYPOINT ["python", "tg_bot.py"]
