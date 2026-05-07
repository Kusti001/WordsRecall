
from aiogram.fsm.context import FSMContext
from states import FeedbackState, ReviewStates, ReportStates

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from api import add_word, get_stats, get_dictionary, is_valid_word, register_user, get_review, get_word, escape_md, send_review 
from keyboards import review_keyboard, add_keyboard, main_keyboard
from config import settings
from messages import (
    REVIEW_START, START_NEW_USER, START_RETURNING_USER, DICTIONARY_EMPTY, DICTIONARY_HEADER, DICTIONARY_ITEM,
    WORD_INVALID, WORD_FOUND_TEMPLATE, WORD_ADDED, WORD_ALREADY_EXISTS,
    REVIEW_NO_WORDS, REVIEW_WORD_TEMPLATE, REVIEW_COMPLETE,
    FEEDBACK_PROMPT, FEEDBACK_CONFIRMATION, FEEDBACK_ADMIN,
    COMING_SOON, CANCELLED,
    ERROR_DICT_FETCH, ERROR_WORDS_FETCH, ERROR_WORD_SEARCH, ERROR_WORD_ADD,
    ERROR_REVIEW_PROCESS, ERROR_REVIEW_INVALID, ERROR_FEEDBACK, ERROR_GENERAL,
    get_api_error_message
)
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    """Handle /start command"""
    try:
        res = await register_user(str(message.from_user.id))
        
        if res.get("error"):
            await message.answer(get_api_error_message(res))
            return
            
        if res.get("message") == "user_created":
            await message.answer((START_NEW_USER), reply_markup=main_keyboard(), parse_mode="MarkdownV2")
        else:
            await message.answer((START_RETURNING_USER), reply_markup=main_keyboard(), parse_mode="MarkdownV2")
            
        logger.info(f"User {message.from_user.id} started")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.answer(ERROR_GENERAL)

@router.message(Command("dictionary"))
@router.message(F.text == "📚 Словарь")
async def get_dictionary_words(message: Message):
    """Get user's complete dictionary"""
    try:
        res = await get_dictionary(str(message.from_user.id))
        
        if res["total"] == 0:
            await message.answer(DICTIONARY_EMPTY)
            return
        
        text = DICTIONARY_HEADER
        for i, word in enumerate(res["items"]):
            text += DICTIONARY_ITEM.format(
                i=i+1,
                word=escape_md(word['word']),
                translation=escape_md(word['translation']),
                next_review=escape_md(word["next_review"])
            )
        
        await message.answer(text, parse_mode="MarkdownV2")
        logger.info(f"User {message.from_user.id} viewed dictionary")
    except Exception as e:
        logger.error(f"Error in get_dictionary_words: {e}")
        await message.answer(ERROR_DICT_FETCH)

@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def stats(message: Message):
    """Show user statistics"""
    try:         
        res =  await get_stats(str(message.from_user.id))
        if res.get("error"):
            await message.answer(get_api_error_message(res))
            return
        
        await message.answer(f"Статистика:\n\nСлов в словаре: {res['data']['total_words']}\nСлов на повторение: {res['data']['review_words']}")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.answer(ERROR_GENERAL)


@router.message(F.text == "⚠️ Обратная связь")
async def feedback(message: Message, state: FSMContext):
    """Start feedback message collection"""
    await state.set_state(FeedbackState.waiting_for_message)
    await message.answer(FEEDBACK_PROMPT)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await message.answer(CANCELLED)


@router.message(FeedbackState.waiting_for_message)
async def feedback_message(message: Message, state: FSMContext):
    """Process feedback message"""
    try:
        await message.bot.send_message(
            settings.ADMIN_ID,
            FEEDBACK_ADMIN.format(
                username=message.from_user.username or 'unknown',
                user_id=message.from_user.id,
                message=message.text
            )
        )
        await state.clear()
        await message.answer(FEEDBACK_CONFIRMATION)
        logger.info(f"Feedback from user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error sending feedback: {e}")
        await message.answer(ERROR_FEEDBACK)


@router.callback_query(F.data.startswith("add:"))
async def confirm_add_word(callback: CallbackQuery):
    """Add word to user's dictionary"""
    try:
        parts = callback.data.split(":")
        word_id = parts[1]
        word_text = parts[2] if len(parts) > 2 else data.get("word", str(word_id))
        
        res = await add_word(str(callback.from_user.id), word_id)
        data = res.get("data", {})
        if res.get("error"):
            await callback.message.answer(get_api_error_message(res))
        elif res.get("message") == "word_added":
            await callback.message.answer(WORD_ADDED.format(word=escape_md(word_text)), parse_mode="MarkdownV2")
            logger.info(f"Word {word_text} added for user {callback.from_user.id}")
        elif res.get("message") == "word_already_exists":
            await callback.message.answer(WORD_ALREADY_EXISTS.format(word=escape_md(word_text)), parse_mode="MarkdownV2")
            logger.info(f"Word {word_text} already exists for user {callback.from_user.id}")
        else:
            await callback.message.answer(WORD_ALREADY_EXISTS.format(word=escape_md(word_text)), parse_mode="MarkdownV2")
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in confirm_add_word: {e}")
        await callback.answer(ERROR_WORD_ADD, show_alert=True)


@router.message(F.text=="🔁 Повторять")
@router.message(Command("get"))  
async def get_review_words(message: Message, state: FSMContext):
    """Get words ready for review"""
    try:
        res = await get_review(str(message.from_user.id))
        
        if res.get("error"):
            await message.answer(get_api_error_message(res))
            return
            
        if res.get("total", 0) == 0:
            await message.answer(REVIEW_NO_WORDS)
            return
        
        message.answer(REVIEW_START)
        words = res.get("items", [])
        
        # Save words list and current index in state
        await state.update_data(
            words=words,
            current_index=0
        )
        await state.set_state(ReviewStates.reviewing)
        
        # Send first word
        if words:
            await send_word(message, words[0])
            logger.info(f"Started review session for user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in get_review_words: {e}")
        await message.answer(ERROR_WORDS_FETCH)

async def send_word(target, word):
    text = REVIEW_WORD_TEMPLATE.format(
        word=escape_md(word['word']),
        level=word['level'],
        meaning=escape_md(word['meaning']),
        example=escape_md(word['example']),
        translation=escape_md(word['translation'])
    )
    
    if isinstance(target, Message):
        await target.answer(text, reply_markup=review_keyboard(word['user_word_id']), parse_mode="MarkdownV2")
    else:  # CallbackQuery
        await target.message.edit_text(text, reply_markup=review_keyboard(word['user_word_id']), parse_mode="MarkdownV2")

@router.callback_query(ReviewStates.reviewing, F.data.startswith("review:"))
async def process_review(callback: CallbackQuery, state: FSMContext):
    """Process word review result"""
    try:
        parts = callback.data.split(":")
        if len(parts) < 3:
            logger.warning(f"Invalid review callback data: {callback.data}")
            await callback.answer(ERROR_REVIEW_INVALID, show_alert=True)
            return
            
        user_word_id = parts[1]
        result = parts[2]
        
        # Record the review result
        res = await send_review(str(callback.from_user.id), user_word_id, result)
        
        if res.get("error"):
            await callback.message.answer(get_api_error_message(res))
            await state.clear()
            await callback.answer()
            return
        
        # Get current state
        data = await state.get_data()
        words = data.get("words", [])
        current_index = data.get("current_index", 0)
        
        logger.info(f"Review recorded for user {callback.from_user.id}: result={result}")
        
        # Move to next word
        if current_index + 1 < len(words):
            await state.update_data(current_index=current_index + 1)
            await send_word(callback, words[current_index + 1])
        else:
            # Review session completed
            await callback.message.answer(REVIEW_COMPLETE)
            await state.clear()
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_review: {e}")
        await callback.answer(ERROR_REVIEW_PROCESS, show_alert=True)
        await state.clear() 

@router.callback_query(F.data.startswith("report:"))
async def report_word_start(callback: CallbackQuery, state: FSMContext):
    """Start report process - ask for user input"""
    try:
        word_id = callback.data.split(":")[1]
        
        # Сохраняем word_id и оригинальный текст в состояние
        await state.update_data(
            word_id=word_id,
            original_text=callback.message.text or callback.message.caption or "Нет текста"
        )
        
        # Устанавливаем состояние ожидания текста
        await state.set_state(ReportStates.waiting_for_report_text)
        
        # Просим пользователя ввести текст репорта
        await callback.message.answer(
            "📝 **Пожалуйста, опишите проблему:**\n\n"
            "Напишите, что именно не так со словом. "
            "Вы можете отменить действие командой /cancel",
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in report_word_start: {e}")
        await callback.answer("❌ Ошибка при начале репорта", show_alert=True)

@router.message(ReportStates.waiting_for_report_text)
async def process_report_text(message: Message, state: FSMContext):
    """Process user's report text and send to admin"""
    try:
        # Получаем сохраненные данные
        user_data = await state.get_data()
        word_id = user_data.get('word_id')
        original_text = user_data.get('original_text')
        report_text = message.text
        
        # ID админского чата
        ADMIN_CHAT_ID = settings.ADMIN_CHAT_ID  # Замените на ваш ID
        
        # Формируем подробное сообщение для админов
        report_message = (
            f"🚨 **НОВЫЙ РЕПОРТ**\n\n"
            f"👤 **Пользователь:** `{message.from_user.id}`\n"
            f"📛 **Имя:** {escape_md(message.from_user.full_name)}\n"
            f"🔗 **Username:** @{message.from_user.username if message.from_user.username else 'Нет'}\n"
            f"🏷️ **ID слова:** `{word_id}`\n\n"
            f"📝 **Текст репорта:**\n```\n{report_text[:500]}\n```\n\n"
            f"📄 **Контекст \\(оригинал\\):**\n```\n{original_text[:300]}\n```\n"
        )
        
        
        # Отправляем в админский чат
        await message.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=report_message,
            parse_mode="MarkdownV2",
        )
        
        # Подтверждаем пользователю
        await message.answer(
            "✅ **Репорт успешно отправлен!**\n\n"
            "Спасибо за помощь в улучшении бота. Администраторы рассмотрят вашу жалобу.",
            parse_mode="Markdown"
        )
        
        # Логируем
        logger.info(f"Report sent by user {message.from_user.id} for word_id {word_id}")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in process_report_text: {e}")
        await message.answer("❌ Произошла ошибка при отправке репорта. Попробуйте позже.")
        await state.clear()


@router.message(F.text)
async def search_word(message: Message):
    """Search for word or create new card"""
    try:
        if not is_valid_word(message.text):
            await message.answer(WORD_INVALID)
            return
        
        res = await get_word(message.text.strip())
        
        if res.get("error"):
            await message.answer(get_api_error_message(res))
            return
        
        data = res.get("data")
        text = WORD_FOUND_TEMPLATE.format(
            word=escape_md(data['word']),
            level=escape_md(data['level']),
            meaning=escape_md(data['meaning']),
            example=escape_md(data['example']),
            translation=escape_md(data['translation'])
        )
        
        await message.answer(text, parse_mode="MarkdownV2", reply_markup=add_keyboard(data['id'], data['word']))
        logger.info(f"User {message.from_user.id} searched word: {message.text.strip()}")
    except Exception as e:
        logger.error(f"Error in search_word: {e}")
        await message.answer(ERROR_WORD_SEARCH)