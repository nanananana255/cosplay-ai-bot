import aiohttp
import json
from io import BytesIO
from config import STABILITY_API_KEY, STABILITY_ENGINE

async def generate_cosplay(
    task_id: str, 
    image_path: str, 
    style: str, 
    user_id: int
) -> str:
    """Основная функция генерации через Stability API"""
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/png"
    }
    
    # Загрузка конфига стилей
    with open("styles.json") as f:
        styles = json.load(f)
    
    style_config = styles.get(style)
    if not style_config:
        raise ValueError(f"Unknown style: {style}")
    
    # Подготовка тела запроса
    data = aiohttp.FormData()
    data.add_field(
        "text_prompts[0][text]", 
        style_config["prompt"]
    )
    data.add_field(
        "text_prompts[0][weight]", 
        "1.0"
    )
    data.add_field(
        "init_image",
        open(image_path, "rb"),
        filename="input.png",
        content_type="image/png"
    )
    
    # Параметры из конфига
    params = {
        "cfg_scale": style_config.get("cfg_scale", 7),
        "steps": style_config.get("steps", 30),
        "style_preset": style_config.get("style_preset")
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.stability.ai/v1/generation/{STABILITY_ENGINE}/image-to-image",
            headers=headers,
            data=data,
            params=params
        ) as response:
            if response.status != 200:
                error = await response.json()
                raise Exception(f"API Error: {error.get('message')}")
            
            # Сохранение результата
            result = await response.read()
            result_url = await upload_to_server(result, f"{user_id}_{task_id}.png")
            return result_url

async def check_generation_status(task_id: str) -> dict:
    """Проверка статуса задачи"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://api-service/status/{task_id}"
        ) as response:
            return await response.json()