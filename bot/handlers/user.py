from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.keyboards import get_main_menu, get_styles_keyboard
from bot.states import UserStates
from bot import dp

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я могу превратить твоё фото в крутой косплей!\n"
        "Отправь мне своё фото и выбери стиль.",
        reply_markup=get_main_menu()
    )

@dp.message_handler(text="🔄 Сделать косплей", state="*")
@dp.message_handler(commands=['generate'], state="*")
async def request_photo(message: types.Message):
    await message.answer("📷 Отправь мне своё фото (портретное лучше всего работает)")
    await UserStates.waiting_for_photo.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=UserStates.waiting_for_photo)
async def handle_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await message.answer("🎨 Выбери стиль косплея:", reply_markup=get_styles_keyboard())
    await UserStates.waiting_for_style.set()