import io
import requests
from bot import Config
from PIL import Image

STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"

async def generate_cosplay_image(photo_bytes: bytes, style_id: str) -> io.BytesIO:
    # Преобразуем фото пользователя
    user_image = Image.open(io.BytesIO(photo_bytes))
    user_image = user_image.resize((512, 512))
    
    # Подготовка промпта в зависимости от стиля
    style_prompts = {
        "anime_samurai": "anime samurai style, intricate armor, vibrant colors, highly detailed",
        "cyberpunk": "cyberpunk character, neon lights, futuristic, cybernetic enhancements",
        "elf": "fantasy elf, pointy ears, magical forest, ethereal beauty",
        "demon": "dark demon, fiery background, horns, menacing expression",
        "jrpg": "JRPG heroine, anime style, fantasy outfit, vibrant colors"
    }
    
    # Отправляем запрос к Stability AI API
    headers = {
        "Authorization": f"Bearer {Config.STABILITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "text_prompts": [{"text": style_prompts[style_id], "weight": 1}],
        "init_image": photo_bytes,
        "image_strength": 0.35,
        "cfg_scale": 7,
        "steps": 30,
        "width": 512,
        "height": 512
    }
    
    response = requests.post(STABILITY_API_URL, headers=headers, json=data)
    response.raise_for_status()
    
    # Обрабатываем результат
    result_bytes = io.BytesIO(response.content)
    return result_bytes