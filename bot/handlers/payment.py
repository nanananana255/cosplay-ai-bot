from aiogram import types
from aiogram.dispatcher import FSMContext
from tonconnect import TonConnect

async def handle_payment(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    style = user_data.get('style')
    
    connector = TonConnect()
    payment_link = connector.create_payment_link(
        amount=5,  # 5 TON
        description=f"Косплей генерация в стиле {style}"
    )
    
    await callback.message.answer(
        "Для продолжения оплатите 5 TON:\n\n"
        f"{payment_link}\n\n"
        "После оплаты нажмите кнопку ниже.",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Я оплатил", callback_data="check_payment")
        )
    )

async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    connector = TonConnect()
    
    if connector.check_payment(user_id):
        await process_generation(callback, state)
    else:
        await callback.answer("Платеж не обнаружен. Попробуйте еще раз.")