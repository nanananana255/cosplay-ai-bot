import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.keyboards import get_after_generation_keyboard
from bot.states import UserStates
from bot.services.stability_api import generate_cosplay_image
from bot.services.database import save_generation, get_user_generations_count
from bot import dp, Config

@dp.callback_query_handler(lambda c: c.data.startswith('style_'), state=UserStates.waiting_for_style)
async def handle_style_selection(callback_query: types.CallbackQuery, state: FSMContext):
    style_id = callback_query.data.split('_')[1]
    user_data = await state.get_data()
    
    generations_count = get_user_generations_count(callback_query.from_user.id)
    if generations_count >= Config.FREE_GENERATIONS_LIMIT:
        await callback_query.message.answer("🚫 Лимит бесплатных генераций исчерпан. Пожалуйста, оплатите следующие.")
        await UserStates.payment.set()
        return
    
    await callback_query.message.edit_text("🔄 Обрабатываю изображение (это займет до 30 секунд)...")
    
    # Получаем файл фото
    photo_file = await callback_query.bot.get_file(user_data['photo_file_id'])
    photo_bytes = await callback_query.bot.download_file(photo_file.file_path)
    
    # Генерируем изображение
    try:
        result_image = await generate_cosplay_image(photo_bytes, style_id)
        await callback_query.bot.send_photo(
            callback_query.from_user.id,
            result_image,
            caption="✨ Ваш косплей готов!",
            reply_markup=get_after_generation_keyboard()
        )
        save_generation(callback_query.from_user.id, style_id)
    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка при генерации: {str(e)}")
    
    await state.finish()