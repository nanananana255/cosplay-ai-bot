from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import main_menu_kb

class UserStates(StatesGroup):
    waiting_for_photo = State()
    choosing_style = State()

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "🎭 Добро пожаловать в CosplayAI!\n\n"
        "Загрузите своё фото, и мы превратим вас в:\n"
        "- Аниме-персонажа\n"
        "- Киберпанк-героя\n"
        "- Фэнтези-героя\n\n"
        "Отправьте фото или сделайте селфи прямо сейчас!",
        reply_markup=main_menu_kb()
    )

async def cmd_help(message: types.Message):
    help_text = (
        "📌 <b>Как это работает:</b>\n"
        "1. Отправьте фото лица (лучше портрет)\n"
        "2. Выберите стиль преобразования\n"
        "3. Получите уникальный косплей-арт!\n\n"
        "🛠 <b>Доступные команды:</b>\n"
        "/start - Перезапустить бота\n"
        "/help - Показать справку\n"
        "/status - Проверить текущую генерацию\n"
        "/history - Посмотреть предыдущие работы"
    )
    await message.answer(help_text, parse_mode="HTML")

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'], state="*")
    dp.register_message_handler(cmd_help, commands=['help'])