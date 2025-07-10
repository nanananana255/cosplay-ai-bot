from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu_kb():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        "🎭 Создать косплей",
        "💎 Мой баланс",
        "👥 Пригласить друзей"
    )

# Выбор стилей
def styles_kb():
    styles = [
        ("Аниме-самурай", "style:anime_samurai"),
        ("Киберпанк", "style:cyberpunk"),
        ("Эльфийка", "style:elf"),
        ("Демон", "style:demon"),
        ("Героиня JRPG", "style:jrpg")
    ]
    kb = InlineKeyboardMarkup(row_width=2)
    for text, data in styles:
        kb.insert(InlineKeyboardButton(text, callback_data=data))
    return kb

# После генерации
def after_generation_kb(task_id: str):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("🔄 Сделать ещё", callback_data=f"again:{task_id}"),
        InlineKeyboardButton("💾 Скачать HD", callback_data=f"download:{task_id}")
    ).row(
        InlineKeyboardButton("📤 Поделиться", switch_inline_query=f"Посмотрите мой косплей! {task_id}")
    )

# Платежная клавиатура
def payment_kb(url: str):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("💳 Оплатить", url=url),
        InlineKeyboardButton("✅ Я оплатил", callback_data="confirm_payment")
    )

# Админ-панель
def admin_kb():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")
    )