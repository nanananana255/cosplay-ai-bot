import sqlite3
from datetime import datetime
from typing import List, Dict

DATABASE = "cosplay.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            join_date TIMESTAMP,
            balance INTEGER DEFAULT 3
        )
        """)
        
        # Таблица генераций
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            task_id TEXT UNIQUE,
            style TEXT,
            result_url TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Таблица платежей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            tx_hash TEXT,
            date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        conn.commit()

def add_user(user: types.User):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (telegram_id, username, join_date) VALUES (?, ?, ?)",
                (user.id, user.username, datetime.now())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Пользователь уже существует

def log_generation(user_id: int, task_id: str, style: str, result_url: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO generations 
            (user_id, task_id, style, result_url, created_at) 
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, task_id, style, result_url, datetime.now())
        )
        conn.commit()

def check_user_balance(user_id: int) -> int:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM users WHERE telegram_id = ?", 
            (user_id,)
        )
        return cursor.fetchone()[0] or 0

def update_balance(user_id: int, delta: int):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
            (delta, user_id)
        )
        conn.commit()

def get_user_stats() -> Dict:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM generations")
        gens = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM payments")
        income = cursor.fetchone()[0] or 0
        
        return {
            "total_users": users,
            "total_generations": gens,
            "total_income": income
        }

def get_user_history(user_id: int, limit=5) -> List[Dict]:
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT style, result_url, created_at 
            FROM generations WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]