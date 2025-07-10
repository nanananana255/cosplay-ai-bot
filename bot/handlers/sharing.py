from aiogram import types
from aiogram.utils.deep_linking import create_start_link
from database import add_referral

async def generate_invite(message: types.Message):
    link = await create_start_link(message.bot, payload=str(message.from_user.id))
    await message.answer(
        "👥 Пригласите друзей и получайте бесплатные генерации!\n\n"
        f"Ваша реферальная ссылка:\n{link}\n\n"
        "За каждого приглашенного друга вы получите +3 генерации",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Поделиться", url=f"tg://msg?text={link}")
        )
    )

async def handle_referral_start(message: types.Message):
    args = message.get_args()
    if args and args.isdigit():
        referrer_id = int(args)
        if referrer_id != message.from_user.id:
            add_referral(referrer_id, message.from_user.id)
            await message.answer(
                "🎉 Вы активировали реферальную ссылку! "
                "Теперь вы и ваш друг получите бонусные генерации."
            )

def register_sharing_handlers(dp: Dispatcher):
    dp.register_message_handler(
        generate_invite, 
        commands=['invite']
    )
    dp.register_message_handler(
        handle_referral_start, 
        commands=['start'],
        commands_ignore_caption=False
    )