import os
import uuid
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import styles_kb, after_generation_kb
from utils import download_image, upload_to_server
from api_client import generate_cosplay

async def handle_photo(message: types.Message, state: FSMContext):
    # Сохраняем фото во временное хранилище
    file_id = message.photo[-1].file_id
    file_path = await download_image(message.bot, file_id)
    
    await state.update_data(photo_path=file_path)
    await UserStates.choosing_style.set()
    
    await message.answer(
        "🖼 Фото получено! Теперь выберите стиль:",
        reply_markup=styles_kb()
    )

async def choose_style(callback: types.CallbackQuery, state: FSMContext):
    style = callback.data.split(":")[1]
    user_data = await state.get_data()
    
    # Создаем уникальный ID задачи
    task_id = str(uuid.uuid4())
    await callback.message.edit_text("🔄 Начинаю генерацию...")
    
    try:
        # Отправляем в API
        result_url = await generate_cosplay(
            task_id=task_id,
            image_path=user_data['photo_path'],
            style=style,
            user_id=callback.from_user.id
        )
        
        await callback.message.answer_photo(
            photo=result_url,
            caption=f"🎉 Ваш {style} косплей готов!",
            reply_markup=after_generation_kb(task_id)
        )
        await state.finish()
        
    except Exception as e:
        await callback.message.answer("⚠️ Ошибка генерации. Попробуйте другое фото.")
        await state.finish()

def register_image_handlers(dp: Dispatcher):
    dp.register_message_handler(
        handle_photo, 
        content_types=['photo'], 
        state=UserStates.waiting_for_photo
    )
    dp.register_callback_query_handler(
        choose_style, 
        lambda c: c.data.startswith('style:'), 
        state=UserStates.choosing_style
    )