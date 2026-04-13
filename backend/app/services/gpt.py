from dotenv import load_dotenv
import json
from google import genai
from google.genai import types   # ← обязательно импортируем для config

# Загружаем переменные окружения (.env)
load_dotenv()

# Создаём клиента (API ключ берётся автоматически из GEMINI_API_KEY)
client = genai.Client()

system_prompt = """
Ты — профессиональный языковой ассистент и создатель словарных карточек.

Пользователь присылает слово или фразу на русском или английском языке.

Твоя задача — всегда отвечать строго в следующем JSON-формате:

{
  "english": "перевод или оригинал на английском",
  "russian": "перевод на русский язык",
  "example": "пример предложения на английском языке с этим словом"
}

Правила:
- Если пользователь прислал слово на английском → "english" содержит это слово, а "russian" — его точный перевод на русский.
- Если пользователь прислал слово на русском → "russian" содержит это слово, а "english" — правильный перевод на английский.
- "example" всегда должен быть естественным, грамматически правильным предложением на английском языке.
- Не добавляй никаких пояснений, тройных кавычек, приветствий, эмодзи или текста вне JSON.
- Всегда возвращай только валидный JSON объект.
"""


def generate_word_data(user_word):
    # Формируем запрос
    response = client.models.generate_content(
        model="gemini-2.5-flash",          # или "gemini-3-flash-preview", если хочешь новее
        contents=user_word,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,               # низкая температура — ответы более стабильные
            max_output_tokens=300
        )
    )
    raw_text = response.text.strip()

    # 2. Очищаем ответ от возможного markdown
    if raw_text.startswith("```json"):
        raw_text = raw_text.split("```json")[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.split("```")[0]

    raw_text = raw_text.strip()

    # 3. Парсим JSON
    word_data = json.loads(raw_text)
    return word_data