# ============ START / WELCOME MESSAGES ============

START_NEW_USER = """👋 Привет\! Я помогу тебе учить английские слова через интервальные повторения\.

🤖 **Как работает бот:**
Ты пишешь слово → получаешь перевод, транскрипцию, пример и meaning на английском → добавляешь в словарь → повторяешь по системе интервальных повторений → учишь новые слова

📚 **Откуда брать слова:**
• Вводишь сам — добавляй сколько хочешь, лимитов нет
• Закончились слова для повторения? бот сам подкинет 5 новых слов в день

👨‍💻 **Что нужно знать обо мне:**
Я работаю один, и у меня сессия\. Поэтому в словарях могут быть ошибки, но я стараюсь 🙃

💬 Предложения и фидбек — @kusti0\_0

\-\-\-

🔹 /get — учить слова 

Пиши любое слово\! 👇"""

START_RETURNING_USER = """С возвращением 👋

🤖 **Как работает бот:**
Ты пишешь слово → получаешь перевод, транскрипцию, пример и meaning на английском → добавляешь в словарь → повторяешь по системе интервальных повторений → учишь новые слова

📚 **Откуда брать слова:**
• Вводишь сам — добавляй сколько хочешь, лимитов нет
• Закончились слова для повторения? бот сам подкинет 5 новых слов в день

👨‍💻 **Что нужно знать обо мне:**
Я работаю один, и у меня сессия\. Поэтому в словарях могут быть ошибки, но я стараюсь 🙃

💬 Предложения и фидбек — @kusti0\_0

"""

# ============ DICTIONARY MESSAGES ============

DICTIONARY_EMPTY = "Словарь пуст. Добавь новые слова, отправив их мне в сообщении."
DICTIONARY_HEADER = "📚 *Твой словарь:*\n\n"
DICTIONARY_ITEM = "{i}\\) *{word}* \\- {translation} следующее повторение: {next_review}\n"

# ============ WORD SEARCH MESSAGES ============

WORD_INVALID = "Пожалуйста, отправь корректное слово (только буквы, не слишком длинное)."
WORD_FOUND_TEMPLATE = (
    "📖 *{word}* `{level}`\n\n"
    "📚 *Definition:*\n_{meaning}_\n\n"
    "💬 *Example:*\n_{example}_\n\n"
    "🇷🇺 *Translation:*\n||{translation}||"
)

# ============ WORD MANAGEMENT MESSAGES ============

WORD_ADDED = "✅ Слово *{word}* добавлено в словарь"
WORD_ALREADY_EXISTS = "⚠️ Слово *{word}* уже в словаре"
REVIEW_NO_WORDS = "Слова для повторения не найдены. Добавь новые слова, отправив их мне в сообщении."
REVIEW_NEW_WORDS = "Нет слов для повторения — вот новые слова для изучения 👇"

# ============ REVIEW MESSAGES ============

REVIEW_WORD_TEMPLATE = (
    "📖 *{word}*, {level}\n\n"
    "📚 *Definition:*\n_{meaning}_\n\n"
    "💬 *Example:*\n_{example}_\n\n"
    "🇷🇺 *Translation:*\n||{translation}||"
)
REVIEW_COMPLETE = "✅ Повторение завершено! Хорошей учёбы! 📚"

# ============ FEEDBACK MESSAGES ============

FEEDBACK_PROMPT = (
    "Напиши своё сообщение👇\n\n"
    "Для отмены напиши /cancel"
)
FEEDBACK_CONFIRMATION = "✅ Сообщение отправлено, спасибо!"
FEEDBACK_TEMPLATE = "📩 Обратная связь\n\nОт: @{username} ({user_id})\n\nСообщение:\n{message}"

# ============ ADMIN NOTIFICATION ============

FEEDBACK_ADMIN = "📩 Обратная связь\n\nОт: @{username} ({user_id})\n\nСообщение:\n{message}"

# ============ FEATURE MESSAGES ============

STATS_COMING_SOON = "Функция в разработке! 👨‍💻"
REPORT_COMING_SOON = "Функция в разработке! 👨‍💻"

# ============ CONFIRMATION MESSAGES ============

CANCELLED = "Отменено 👌"

# ============ ERROR MESSAGES ============

ERROR_DICT_FETCH = "❌ Ошибка получения словаря."
ERROR_WORDS_FETCH = "❌ Ошибка получения слов для повторения."
ERROR_WORD_SEARCH = "❌ Ошибка поиска слова."
ERROR_WORD_ADD = "❌ Ошибка добавления слова"
ERROR_REVIEW_PROCESS = "❌ Ошибка обработки ответа"
ERROR_REVIEW_INVALID = "❌ Ошибка обработки ответа"
ERROR_FEEDBACK = "❌ Ошибка отправки сообщения."
ERROR_GENERAL = "❌ Что-то пошло не так. Попробуй позже."

# ============ API ERROR MESSAGES ============

API_ERROR_CONNECTION = "❌ Сервер недоступен. Попробуй позже."
API_ERROR_TIMEOUT = "⏱️ Сервер не отвечает. Попробуй позже."
API_ERROR_NOT_FOUND = "❌ Ошибка: не найдено."
API_ERROR_BAD_REQUEST = "❌ Неверный запрос."
API_ERROR_SERVER = "❌ Ошибка сервера. Сообщи администратору."
API_ERROR_UNKNOWN = "❌ Неизвестная ошибка. Попробуй позже."

# ============ KEYBOARD LABELS ============

BUTTON_DICTIONARY = "📚 Словарь"
BUTTON_STATS = "📊 Статистика"
BUTTON_FEEDBACK = "⚠️ Обратная связь"
BUTTON_REVIEW = "🔁 Повторять"

# ============ HELPER FUNCTIONS ============

def get_api_error_message(error: dict) -> str:
    """Convert API error to user-friendly message"""
    error_type = error.get("error")
    
    if error_type == "connection_failed":
        return API_ERROR_CONNECTION
    elif error_type == "timeout":
        return API_ERROR_TIMEOUT
    elif error_type == "not_found":
        return API_ERROR_NOT_FOUND
    elif error_type == "bad_request":
        return API_ERROR_BAD_REQUEST
    elif error_type == "server_error":
        return API_ERROR_SERVER
    else:
        return API_ERROR_UNKNOWN
