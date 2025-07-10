from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config

def get_main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("🔄 Сделать косплей")
    )

def get_styles_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for style_id, style_name in Config.STYLES.items():
        keyboard.insert(InlineKeyboardButton(style_name, callback_data=f"style_{style_id}"))
    return keyboard

def get_after_generation_keyboard():
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("⬇️ Скачать HD", callback_data="download_hd"),
        InlineKeyboardButton("🔄 Сделать ещё", callback_data="generate_more")
    ).row(
        InlineKeyboardButton("📤 Поделиться", callback_data="share")
    )