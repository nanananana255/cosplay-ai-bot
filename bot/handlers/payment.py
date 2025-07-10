from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.services.database import get_user_generations_count
from bot.services.payment import PaymentService, StripePayment
from bot import dp, Config
from bot.states import UserStates
from bot.keyboards import get_styles_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_service = PaymentService()

async def request_photo(message: types.Message):
    await message.answer("📷 Отправь мне своё фото (портретное лучше всего работает)")
    await UserStates.waiting_for_photo.set()

@dp.callback_query_handler(text="generate_more", state="*")
async def handle_generate_more(callback_query: types.CallbackQuery):
    generations_count = get_user_generations_count(callback_query.from_user.id)
    if generations_count >= Config.FREE_GENERATIONS_LIMIT:
        await callback_query.message.answer("💳 Пожалуйста, оплатите следующие генерации:")
        await handle_payment(callback_query.message)
        await UserStates.payment.set()
    else:
        await request_photo(callback_query.message)

async def handle_payment(message: types.Message):
    # TON Connect вариант
    payment_url = await payment_service.create_ton_payment_link(
        message.from_user.id, 
        amount=5.0  # 5 TON
    )
    
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("💎 Оплатить через TON", url=payment_url),
        InlineKeyboardButton("💳 Оплатить картой", callback_data="stripe_payment")
    )
    
    await message.answer(
        "🔮 Выберите способ оплаты:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(text="stripe_payment")
async def handle_stripe_payment(callback: types.CallbackQuery):
    payment_url = await StripePayment.create_checkout_session(callback.from_user.id)
    await callback.message.answer(
        "Перейдите по ссылке для оплаты:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Оплатить картой", url=payment_url)
        )
    )

@dp.callback_query_handler(lambda c: c.data == "download_hd", state="*")
async def handle_download_hd(callback_query: types.CallbackQuery):
    # Здесь будет логика для скачивания HD версии
    await callback_query.answer("HD версия будет доступна после оплаты", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "share", state="*")
async def handle_share(callback_query: types.CallbackQuery):
    await callback_query.answer("Ссылка для приглашения друзей скопирована в буфер обмена!", show_alert=False)
    # Логика генерации реферальной ссылки
    ref_link = f"https://t.me/{callback_query.bot.username}?start=ref_{callback_query.from_user.id}"
    await callback_query.message.answer(
        f"👋 Пригласите друзей! Ваша ссылка:\n{ref_link}\n\n"
        "За каждого приглашенного друга вы получите +1 бесплатная генерация!"
    )

# Webhook обработчик для Stripe (должен быть в API, но регистрация здесь)
@dp.message_handler(content_types=types.ContentType.WEBHOOK, state="*")
async def handle_stripe_webhook(message: types.Message):
    try:
        event = await StripePayment.verify_webhook(
            message.get_payload(),
            message.headers.get('Stripe-Signature')
        )
        
        if event['type'] == 'checkout.session.completed':
            user_id = event['data']['object']['metadata']['user_id']
            # Логика обработки успешной оплаты
            await dp.bot.send_message(
                user_id,
                "✅ Оплата прошла успешно! Теперь вы можете сделать больше генераций."
            )
            
    except Exception as e:
        print(f"Stripe webhook error: {e}")