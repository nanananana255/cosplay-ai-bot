from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
    FREE_GENERATIONS_LIMIT = 10
    
    STYLES = {
        "anime_samurai": "Anime Samurai Style",
        "cyberpunk": "Cyberpunk Hero",
        "elf": "Fantasy Elf",
        "demon": "Dark Demon",
        "jrpg": "JRPG Heroine"
    }

bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)