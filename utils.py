import os
from aiogram import Bot
from PIL import Image
import numpy as np
import cv2

async def download_image(bot: Bot, file_id: str) -> str:
    """Скачивание файла из Telegram"""
    file = await bot.get_file(file_id)
    path = f"temp/{file_id}.jpg"
    await bot.download_file(file.file_path, path)
    return path

async def upload_to_server(image_data: bytes, filename: str) -> str:
    """Загрузка изображения на сервер (заглушка)"""
    path = f"results/{filename}"
    with open(path, "wb") as f:
        f.write(image_data)
    return f"https://yourdomain.com/{path}"

def preprocess_image(image_path: str) -> str:
    """Предварительная обработка изображения"""
    img = cv2.imread(image_path)
    
    # Детекция лица (упрощенный пример)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        cropped = img[y:y+h, x:x+w]
    else:
        cropped = img  # Если лицо не найдено
    
    # Ресайз под модель
    processed = cv2.resize(cropped, (512, 512))
    processed_path = f"processed_{os.path.basename(image_path)}"
    cv2.imwrite(processed_path, processed)
    
    return processed_path

def cleanup_files(*paths):
    """Удаление временных файлов"""
    for path in paths:
        try:
            os.remove(path)
        except:
            pass