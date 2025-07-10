import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.start import register_start_handlers
from handlers.image_processing import register_image_handlers
from handlers.payment import register_payment_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Form(StatesGroup):
    waiting_for_photo = State()
    choosing_style = State()
    processing = State()

async def on_startup(dp: Dispatcher):
    await bot.set_webhook(os.getenv('WEBHOOK_URL'))

async def on_shutdown(dp: Dispatcher):
    await bot.delete_webhook()

def main():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_start_handlers(dp)
    register_image_handlers(dp)
    register_payment_handlers(dp)

    if os.getenv('WEBHOOK_MODE') == 'True':
        from aiogram.utils.executor import start_webhook
        start_webhook(
            dispatcher=dp,
            webhook_path='/webhook',
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host='0.0.0.0',
            port=int(os.getenv('WEBHOOK_PORT', 8443)),
        )
    else:
        from aiogram.utils.executor import start_polling
        start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()  