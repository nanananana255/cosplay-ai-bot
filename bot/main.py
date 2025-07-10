import asyncio
from aiogram import executor
from bot import dp
from bot.handlers import register_all_handlers
from bot.middlewares.throttling import ThrottlingMiddleware

async def on_startup(dp):
    await dp.bot.set_my_commands([
        {"command": "start", "description": "Запустить бота"},
        {"command": "generate", "description": "Создать косплей"}
    ])
    print("Бот запущен")

if __name__ == '__main__':
    # Регистрация middleware
    dp.middleware.setup(ThrottlingMiddleware())
    
    # Регистрация обработчиков
    register_all_handlers(dp)
    
    # Запуск бота
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)