
from aiogram.fsm.context import FSMContext
from states import FeedbackState

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from api import is_valid_word, register_user, get_review, get_word,escape_md 
from keyboards import review_keyboard, add_keyboard, main_keyboard

router = Router()
ADMIN_ID = 1097433499

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

@router.message(F.text=="🔁 Повторять")
@router.message(Command("get"))  
async def get_review_words(message: Message):
    res = await get_review(str(message.from_user.id))
    if res["total"] == 0:
        await message.answer("Слова для повторения не найдены. Добавь новые слова, отправив их мне в сообщении.")
        return
    
    for word in res["words"]:
        text = f"Слово: {word['word']}\nПеревод: {word['translation']}\nПример: {word['example']}"
        await message.answer(text, reply_markup=review_keyboard(word['user_word_id']))

@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def add_word(message: Message):
    await message.answer("Функция в разработке! <3", show_alert=False)

@router.message(F.text == "⚠️ Обратная связь")
async def feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackState.waiting_for_message)
    await message.answer(
        "Напиши своё сообщение👇\n\n"
        "Для отмены напиши /cancel"
    )

@router.message(FeedbackState.waiting_for_message)
async def feedback_message(message: Message, state: FSMContext):
    await message.bot.send_message(
        ADMIN_ID,
        f"📩 Обратная связь\n\n"
        f"От: @{message.from_user.username} ({message.from_user.id})\n\n"
        f"Сообщение:\n{message.text}"
    )
    await state.clear()
    await message.answer("✅ Сообщение отправлено, спасибо!")

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено 👌")



@router.callback_query(F.data.startswith("add:"))
async def confirm_add_word(callback: CallbackQuery):
    # word_id = callback.data.split(":")[1]
    
    # res = await add_word_api(str(callback.from_user.id), word_id)
    
    #await callback.message.edit_reply_markup(reply_markup=None)
    #await callback.answer("✅ Добавлено в словарь", show_alert=False)
    await callback.answer("Функция в разработке! <3", show_alert=False)


@router.callback_query(F.data.startswith("report:"))
async def report_word(callback: CallbackQuery):
    # word_id = callback.data.split(":")[1]
    
    # res = await add_word_api(str(callback.from_user.id), word_id)
    
    #await callback.message.edit_reply_markup(reply_markup=None)
    #await callback.answer("✅ Добавлено в словарь", show_alert=False)
    await callback.answer("Функция в разработке! <3", show_alert=False)









@router.message(F.text)
async def add_word(message: Message):
    if not is_valid_word(message.text):
        await message.answer("Пожалуйста, отправь корректное слово (только буквы, не слишком длинное).")
        return
    word_data = await get_word(message.text.strip())
    text = (
    f"📖 *{escape_md(word_data['word'])}*, {word_data['level']}\n\n"
    f"📚 *Definition:\n *\{escape_md(word_data['meaning'])}\n\n"
    f"💬 *Example:\n *{escape_md(word_data['example'])}\n\n"
    f"🇷🇺 *Translation:*\n||{escape_md(word_data['translation'])}||"
)

    await message.answer(text, parse_mode="MarkdownV2", reply_markup=add_keyboard(word_data['id']))