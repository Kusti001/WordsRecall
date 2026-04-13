from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from api import register_user, add_word, get_review, send_review
from keyboards import review_keyboard

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await register_user(str(message.from_user.id))
    await message.answer("Привет! Напиши слово чтобы добавить его в учёбу, или /review чтобы повторять.")

@router.message(Command("review"))
async def review(message: Message):
    data = await get_review(str(message.from_user.id))
    words = data.get("words", [])
    
    if not words:
        await message.answer("Слов на повторение нет 🎉")
        return
    
    # показываем первое слово
    word = words[0]
    await message.answer(
        f"🔤 {word['word']}\n\nКак ты знаешь это слово?",
        reply_markup=review_keyboard(word["user_word_id"])
    )

@router.callback_query(F.data.startswith("review:"))
async def handle_review(callback: CallbackQuery):
    _, user_word_id, result = callback.data.split(":")
    
    await send_review(str(callback.from_user.id), int(user_word_id), result)
    await callback.message.edit_text(f"Записал! Следующее повторение скоро.")
    await callback.answer()

# любое текстовое сообщение = новое слово
@router.message(F.text)
async def add_new_word(message: Message):
    data = await add_word(str(message.from_user.id), message.text.strip())
    
    if data["message"] == "already_exists":
        await message.answer(f"Ты уже учишь слово «{message.text}»")
        return
    
    await message.answer(
        f"✅ Добавлено!\n\n"
        f"🔤 {data['word']}\n"
        f"🇷🇺 {data['translation']}\n"
        f"📝 {data.get('example', '—')}"
    )