from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_user_stats, get_generation_logs

def register_admin_handlers(dp: Dispatcher):
    @dp.message_handler(commands=['stats'], is_admin=True)
    async def admin_stats(message: types.Message):
        stats = get_user_stats()
        await message.answer(
            f"📊 Статистика:\n\n"
            f"👥 Пользователей: {stats['total_users']}\n"
            f"🔄 Генераций: {stats['total_generations']}\n"
            f"💰 Доход: {stats['total_income']} TON"
        )
    
    @dp.message_handler(commands=['logs'], is_admin=True)
    async def admin_logs(message: types.Message):
        logs = get_generation_logs(limit=10)
        log_text = "\n".join(
            f"{log['date']} - {log['user_id']} - {log['style']} - {log['status']}"
            for log in logs
        )
        await message.answer(f"📝 Последние генерации:\n\n{log_text}")