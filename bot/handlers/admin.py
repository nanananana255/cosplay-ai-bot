from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.services.database import get_all_users, get_all_generations
from bot import dp, Config

@dp.message_handler(commands=['admin'], user_id=Config.ADMIN_IDS)
async def admin_panel(message: types.Message):
    await message.answer(
        "👨‍💻 Панель администратора:\n"
        "/users - Список пользователей\n"
        "/stats - Статистика генераций"
    )

@dp.message_handler(commands=['users'], user_id=Config.ADMIN_IDS)
async def show_users(message: types.Message):
    users = get_all_users()
    await message.answer(f"👥 Всего пользователей: {len(users)}\n\n" + "\n".join(
        f"{user.id}: {user.first_name} ({user.generations_count} генераций)"
        for user in users
    ))