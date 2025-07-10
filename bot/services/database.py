import sqlite3
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "cosplay_bot.db"

@dataclass
class User:
    id: int
    first_name: str
    generations_count: int

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            generations_count INTEGER DEFAULT 0
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            style TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

def save_generation(user_id: int, style: str):
    with sqlite3.connect(DB_PATH) as conn:
        # Добавляем или обновляем пользователя
        conn.execute(
            "INSERT OR IGNORE INTO users (id, first_name) VALUES (?, ?)",
            (user_id, "Unknown")
        )
        conn.execute(
            "UPDATE users SET generations_count = generations_count + 1 WHERE id = ?",
            (user_id,)
        )
        # Сохраняем генерацию
        conn.execute(
            "INSERT INTO generations (user_id, style) VALUES (?, ?)",
            (user_id, style)
        )

def get_user_generations_count(user_id: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT generations_count FROM users WHERE id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0

def get_all_users() -> list[User]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, first_name, generations_count FROM users"
        )
        return [User(*row) for row in cursor.fetchall()]

def get_all_generations():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT user_id, style, timestamp FROM generations ORDER BY timestamp DESC"
        )
        return cursor.fetchall()

# Инициализация БД при импорте
init_db()