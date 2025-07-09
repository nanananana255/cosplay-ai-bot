import os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp
import json

logging.basicConfig(level=logging.INFO)

API_URL = os.getenv('API_URL', 'http://api:8000')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Стили для косплея
STYLES = {
    'anime_samurai': {'name': 'Аниме-самурай', 'emoji': '🗡'},
    'cyberpunk': {'name': 'Киберпанк-герой', 'emoji': '👾'},
    'elf': {'name': 'Эльфийка', 'emoji': '🧝'},
    'demon': {'name': 'Демон', 'emoji': '👹'},
    'jrpg': {'name': 'Героиня JRPG', 'emoji': '🎮'}
}

class UserStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_style = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "👋 Привет! Я могу превратить твое фото в крутой косплей-образ.\n"
        "Просто отправь мне свое фото и выбери стиль!",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message, state: FSMContext):
    await UserStates.waiting_for_style.set()
    
    # Сохраняем фото
    photo_id = message.photo[-1].file_id
    file_path = await bot.get_file(photo_id)
    photo_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path.file_path}"
    
    await state.update_data(photo_url=photo_url)
    
    # Создаем клавиатуру с выбором стиля
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for style_id, style_data in STYLES.items():
        keyboard.add(types.KeyboardButton(f"{style_data['emoji']} {style_data['name']}"))
    
    await message.reply("Отлично! Теперь выбери стиль для косплея:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in [f"{v['emoji']} {v['name']}" for v in STYLES.values()], state=UserStates.waiting_for_style)
async def handle_style(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photo_url = user_data['photo_url']
    
    # Определяем выбранный стиль
    selected_style = None
    for style_id, style_data in STYLES.items():
        if message.text == f"{style_data['emoji']} {style_data['name']}":
            selected_style = style_id
            break
    
    if not selected_style:
        await message.reply("Произошла ошибка. Пожалуйста, попробуй еще раз.")
        await state.finish()
        return
    
    # Отправляем запрос на генерацию
    processing_msg = await message.reply("🔄 Обрабатываю изображение (это займет до 30 секунд)...", reply_markup=types.ReplyKeyboardRemove())
    
    async with aiohttp.ClientSession() as session:
        payload = {
            'user_id': message.from_user.id,
            'photo_url': photo_url,
            'style': selected_style,
            'telegram_message_id': processing_msg.message_id
        }
        
        try:
            async with session.post(f"{API_URL}/generate", json=payload) as resp:
                if resp.status != 200:
                    raise Exception(await resp.text())
                
                response = await resp.json()
                if not response.get('success'):
                    raise Exception(response.get('error', 'Unknown error'))
                
        except Exception as e:
            logging.error(f"Generation error: {str(e)}")
            await processing_msg.edit_text("😔 Произошла ошибка при генерации. Пожалуйста, попробуй еще раз.")
            await state.finish()
            return
    
    # Состояние завершено
    await state.finish()

@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    logging.error(f"Update {update} caused error {exception}")
    return True

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)