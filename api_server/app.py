from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import logging
import os
import sqlite3
from datetime import datetime
import uuid
from tonconnect.connector import Connector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
SD_SERVER_URL = os.getenv('SD_SERVER_URL', 'http://sd_server:8188')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

TON_CONNECT_MANIFEST = {
    "url": "https://yourdomain.com",
    "name": "Cosplay AI Bot",
    "iconUrl": "https://yourdomain.com/icon.png"
}

# Инициализация БД
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        created_at TEXT,
        generations_left INTEGER DEFAULT 10
    )
    ''')
    
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
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ton_sessions (
        user_id INTEGER PRIMARY KEY,
        session_id TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

class GenerationRequest(BaseModel):
    user_id: int
    photo_url: str
    style: str
    telegram_message_id: int

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    # Проверяем/создаем пользователя
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute('SELECT generations_left FROM users WHERE user_id = ?', (request.user_id,))
    user = cursor.fetchone()
    
    if not user:
        # Получаем информацию о пользователе из Telegram
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TELEGRAM_API_URL}getChat?chat_id={request.user_id}") as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail="Cannot get user info from Telegram")
                
                user_info = await resp.json()
                if not user_info.get('ok'):
                    raise HTTPException(status_code=400, detail="Invalid user info from Telegram")
                
                user_data = user_info['result']
                cursor.execute(
                    'INSERT INTO users (user_id, username, first_name, last_name, created_at, generations_left) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        request.user_id,
                        user_data.get('username'),
                        user_data.get('first_name'),
                        user_data.get('last_name'),
                        datetime.now().isoformat(),
                        10  # Начальное количество бесплатных генераций
                    )
                )
                conn.commit()
                generations_left = 10
    else:
        generations_left = user[0]
    
    if generations_left <= 0:
        raise HTTPException(status_code=403, detail="No generations left. Please pay for more.")
    
    # Создаем запись о генерации
    generation_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO generations (id, user_id, style, original_photo_url, created_at, status) VALUES (?, ?, ?, ?, ?, ?)',
        (generation_id, request.user_id, request.style, request.photo_url, datetime.now().isoformat(), 'pending')
    )
    conn.commit()
    
    # Уменьшаем количество доступных генераций
    cursor.execute(
        'UPDATE users SET generations_left = generations_left - 1 WHERE user_id = ?',
        (request.user_id,)
    )
    conn.commit()
    conn.close()
    
    # Отправляем задание в Stable Diffusion
    async with aiohttp.ClientSession() as session:
        payload = {
            "prompt": f"cosplay as {request.style}, high quality, detailed face, intricate costume",
            "negative_prompt": "low quality, blurry, bad anatomy",
            "image_url": request.photo_url,
            "width": 768,
            "height": 768,
            "num_inference_steps": 30,
            "style_preset": request.style
        }
        
        try:
            async with session.post(f"{SD_SERVER_URL}/generate", json=payload) as resp:
                if resp.status != 200:
                    raise Exception(await resp.text())
                
                result = await resp.json()
                if not result.get('success'):
                    raise Exception(result.get('error', 'Unknown error from SD server'))
                
                # Сохраняем результат в БД
                conn = sqlite3.connect('db.sqlite3')
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE generations SET result_photo_url = ?, status = ? WHERE id = ?',
                    (result['image_url'], 'completed', generation_id)
                )
                conn.commit()
                conn.close()
                
                # Отправляем результат пользователю
                async with aiohttp.ClientSession() as tg_session:
                    await tg_session.post(
                        f"{TELEGRAM_API_URL}sendPhoto",
                        json={
                            "chat_id": request.user_id,
                            "photo": result['image_url'],
                            "caption": f"Готово! Твой косплей в стиле {STYLES[request.style]['name']}",
                            "reply_markup": {
                                "inline_keyboard": [
                                    [
                                        {"text": "Скачать в HD", "callback_data": f"download_{generation_id}"},
                                        {"text": "Сделать ещё", "callback_data": f"again_{generation_id}"}
                                    ],
                                    [
                                        {"text": "Поделиться", "callback_data": f"share_{generation_id}"}
                                    ]
                                ]
                            }
                        }
                    )
                
                return {"success": True, "generation_id": generation_id}
        
        except Exception as e:
            logging.error(f"SD generation error: {str(e)}")
            
            # Обновляем статус в БД
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE generations SET status = ? WHERE id = ?',
                ('failed', generation_id)
            )
            conn.commit()
            conn.close()
            
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/ton/connect")
async def get_ton_connect_url(user_id: int):
    connector = Connector(TON_CONNECT_MANIFEST)
    url = connector.connect(
        bridge_url='https://bridge.tonapi.io/bridge',
        wallet_app='tonconnect'
    )
    
    # Сохраняем сессию для пользователя
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO ton_sessions (user_id, session_id) VALUES (?, ?)',
        (user_id, connector.session_id)
    )
    conn.commit()
    conn.close()
    
    return {"url": url}

@app.post("/ton/check")
async def check_ton_payment(user_id: int):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT session_id FROM ton_sessions WHERE user_id = ?', (user_id,))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    connector = Connector(TON_CONNECT_MANIFEST, session_id=session[0])
    if connector.connected:
        # Проверяем баланс
        wallet_address = connector.account.address
        # Здесь должна быть логика проверки платежа
        
        # Если платеж подтвержден
        cursor.execute(
            'UPDATE users SET generations_left = generations_left + 10 WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "generations_added": 10}
    
    conn.close()
    return {"success": False, "error": "Not connected"}

@app.get("/admin/users")
async def get_users():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, first_name, last_name, created_at, generations_left FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return {
        "users": [
            {
                "user_id": user[0],
                "username": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "created_at": user[4],
                "generations_left": user[5]
            }
            for user in users
        ]
    }

@app.get("/admin/generations")
async def get_generations(user_id: int = None):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('SELECT id, user_id, style, status, created_at FROM generations WHERE user_id = ?', (user_id,))
    else:
        cursor.execute('SELECT id, user_id, style, status, created_at FROM generations')
    
    generations = cursor.fetchall()
    conn.close()
    
    return {
        "generations": [
            {
                "id": gen[0],
                "user_id": gen[1],
                "style": gen[2],
                "status": gen[3],
                "created_at": gen[4]
            }
            for gen in generations
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)