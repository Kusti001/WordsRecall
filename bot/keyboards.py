from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def review_keyboard(user_word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Забыл", callback_data=f"review:{user_word_id}:again"),
        InlineKeyboardButton(text="😐 Сложно", callback_data=f"review:{user_word_id}:hard"),
        InlineKeyboardButton(text="✅ Хорошо", callback_data=f"review:{user_word_id}:good"),
        InlineKeyboardButton(text="🔥 Легко", callback_data=f"review:{user_word_id}:easy"),
    ]])