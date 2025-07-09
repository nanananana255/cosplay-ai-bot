FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements первым для кэширования
COPY api_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов
COPY api_server/ .
COPY scripts/setup_db.py /scripts/

# Создание volume для БД
VOLUME /app/db.sqlite3

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]