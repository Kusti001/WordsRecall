from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔁 Повторять")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📚 Словарь")],
            [KeyboardButton(text="⚠️ Обратная связь")],
        ],
        resize_keyboard=True,
        persistent=True  # всегда висит снизу
    )

def review_keyboard(user_word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Забыл", callback_data=f"review:{user_word_id}:again"),
            InlineKeyboardButton(text="😐 Сложно", callback_data=f"review:{user_word_id}:hard"),
            InlineKeyboardButton(text="✅ Легко", callback_data=f"review:{user_word_id}:good"),
        ],
        [
            InlineKeyboardButton(text="⚠️ Ошибка в карточке", callback_data=f"report:{user_word_id}"),
        ]
    ])


def add_keyboard(user_word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить в словарь", callback_data=f"add:{user_word_id}"),
        ],
        [
            InlineKeyboardButton(text="⚠️ Ошибка в карточке", callback_data=f"report:{user_word_id}"),
        ]
    ])

