
from aiogram.fsm.context import FSMContext
from states import FeedbackState, ReviewStates

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from api import add_word, is_valid_word, register_user, get_review, get_word,escape_md, send_review 
from keyboards import review_keyboard, add_keyboard, main_keyboard
from config import settings

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    res = await register_user(str(message.from_user.id))
    if res["message"] == "user_created":
        await message.answer('''Привет 👋

Я помогу тебе учить английские слова через интервальные повторения.

Просто пиши слово — я найду его или создам карточку.

/get — учить слова
/stats — твой прогресс''',reply_markup=main_keyboard())
    else:
        await message.answer('''С возвращением 👋

/get — учить слова
/stats — твой прогресс''',reply_markup=main_keyboard())


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def stats(message: Message):
    await message.answer("Функция в разработке! <3", show_alert=False)

@router.message(F.text == "⚠️ Обратная связь")
async def feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackState.waiting_for_message)
    await message.answer(
        "Напиши своё сообщение👇\n\n"
        "Для отмены напиши /cancel"
    )

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено 👌")

@router.message(FeedbackState.waiting_for_message)
async def feedback_message(message: Message, state: FSMContext):
    await message.bot.send_message(
        settings.ADMIN_ID,
        f"📩 Обратная связь\n\n"
        f"От: @{message.from_user.username} ({message.from_user.id})\n\n"
        f"Сообщение:\n{message.text}"
    )
    await state.clear()
    await message.answer("✅ Сообщение отправлено, спасибо!")


@router.callback_query(F.data.startswith("add:"))
async def confirm_add_word(callback: CallbackQuery):
    word_id = callback.data.split(":")[1]
    
    res = await add_word(str(callback.from_user.id), word_id)
    if res["message"] == "word_added":
        await callback.message.answer(f"✅ Слово {res['word']} добавлено в словарь")
    else:
        await callback.message.answer(f"❌ Слово {res['word']} уже добавлено в словарь", show_alert=False)


@router.message(F.text=="🔁 Повторять")
@router.message(Command("get"))  
async def get_review_words(message: Message, state: FSMContext):
    res = await get_review(str(message.from_user.id))
    if res["total"] == 0:
        await message.answer("Слова для повторения не найдены. Добавь новые слова, отправив их мне в сообщении.")
        return
    
    # Сохраняем список слов и текущий индекс в состоянии
    await state.update_data(
        words=res["words"],
        current_index=0
    )
    await state.set_state(ReviewStates.reviewing)
    
    # Отправляем первое слово
    await send_word(message, res["words"][0])

async def send_word(target, word):
    text = (
        f"📖 *{escape_md(word['word'])}*, {word['level']}\n\n"
        f"📚 *Definition:\n *{escape_md(word['meaning'])}\n\n"
        f"💬 *Example:\n *{escape_md(word['example'])}\n\n"
        f"🇷🇺 *Translation:*\n||{escape_md(word['translation'])}||"
    )
    
    if isinstance(target, Message):
        await target.answer(text, reply_markup=review_keyboard(word['user_word_id']), parse_mode="MarkdownV2")
    else:  # CallbackQuery
        await target.message.edit_text(text, reply_markup=review_keyboard(word['user_word_id']), parse_mode="MarkdownV2")

@router.callback_query(ReviewStates.reviewing, F.data.startswith("review:"))
async def process_review(callback: CallbackQuery, state: FSMContext):
    user_word_id, result = callback.data.split(":")[1:3]
    
    # Сохраняем результат
    await send_review(str(callback.from_user.id), user_word_id, result)
    
    # Получаем текущее состояние
    data = await state.get_data()
    words = data["words"]
    current_index = data["current_index"]
    
    # Переходим к следующему слову
    if current_index + 1 < len(words):
        # Есть следующее слово
        await state.update_data(current_index=current_index + 1)
        await send_word(callback, words[current_index + 1])
        await callback.answer()
    else:
        # Повторение завершено
        await callback.message.answer("✅ Повторение завершено!")
        await state.clear()
        await callback.answer() 

@router.callback_query(F.data.startswith("report:"))
async def report_word(callback: CallbackQuery):
    await callback.answer("Функция в разработке! <3", show_alert=False)

@router.message(F.text)
async def search_word(message: Message):
    if not is_valid_word(message.text):
        await message.answer("Пожалуйста, отправь корректное слово (только буквы, не слишком длинное).")
        return
    word_data = await get_word(message.text.strip())
    text = (
    f"📖 *{escape_md(word_data['word'])}*, {word_data['level']}\n\n"
    f"📚 *Definition:\n *{escape_md(word_data['meaning'])}\n\n"
    f"💬 *Example:\n *{escape_md(word_data['example'])}\n\n"
    f"🇷🇺 *Translation:*\n||{escape_md(word_data['translation'])}||")
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=add_keyboard(word_data['id']))