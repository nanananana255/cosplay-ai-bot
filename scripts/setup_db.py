import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        created_at TEXT,
        generations_left INTEGER DEFAULT 10,
        is_admin BOOLEAN DEFAULT FALSE
    )
    ''')
    
    # Создание таблицы генераций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generations (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        style TEXT,
        original_photo_url TEXT,
        result_photo_url TEXT,
        created_at TEXT,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    ''')
    
    # Создание таблицы платежей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        currency TEXT,
        status TEXT,
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Добавление администратора (если нужно)
    admin_id = input("Введите ID администратора Telegram (оставьте пустым чтобы пропустить): ")
    if admin_id:
        cursor.execute(
            'INSERT OR IGNORE INTO users (user_id, is_admin, created_at) VALUES (?, ?, ?)',
            (int(admin_id), True, datetime.now().isoformat())
        )
    
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована")

if __name__ == '__main__':
    init_db()