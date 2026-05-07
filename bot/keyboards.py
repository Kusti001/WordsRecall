from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from messages import BUTTON_DICTIONARY, BUTTON_FEEDBACK, BUTTON_REVIEW, BUTTON_STATS

def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTON_REVIEW)],
            [KeyboardButton(text=BUTTON_STATS), KeyboardButton(text=BUTTON_DICTIONARY)],
            [KeyboardButton(text=BUTTON_FEEDBACK)],
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


def add_keyboard(word_id: int, word_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить в словарь", callback_data=f"add:{word_id}:{word_text}"),
        ],
        [
            InlineKeyboardButton(text="⚠️ Ошибка в карточке", callback_data=f"report:{word_id}:{word_text}"),
        ]
    ])

