FROM python:3.9-slim

WORKDIR /app

COPY telegram_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_bot/ .

VOLUME /app/logs

CMD ["python", "bot.py"]