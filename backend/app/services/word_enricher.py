import json
import asyncio
from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


client = genai.Client()

class WordEnricher:
    """Обогащает данные слов через GPT батчами"""
    
    @staticmethod
    async def enrich_words(words: list[dict], batch_size: int = 10) -> list[dict]:
        """
        Обогащает слова которым не хватает translation и/или meaning
        Обрабатывает батчами чтобы не перегрузить API
        """
        enriched = []
        
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            
            # Фильтруем слова у которых есть пробелы
            needs_enrichment = [w for w in batch if not w.get("translation") or not w.get("meaning")]
            
            if not needs_enrichment:
                enriched.extend(batch)
                continue
            
            print(f"🔄 Батч {i // batch_size + 1}: обогащаю {len(needs_enrichment)} из {len(batch)} слов")
            
            # Запрашиваем GPT для всего батча
            enriched_data = await WordEnricher._call_gpt(needs_enrichment)
            
            # Мержим результаты
            enriched_dict = {w["word"].lower(): w for w in enriched_data}
            
            for word_obj in batch:
                if word_obj["word"].lower() in enriched_dict:
                    # Заполняем пропущенные поля
                    gpt_data = enriched_dict[word_obj["word"].lower()]
                    if not word_obj.get("translation"):
                        word_obj["translation"] = gpt_data.get("translation")
                    if not word_obj.get("meaning"):
                        word_obj["meaning"] = gpt_data.get("meaning")
                
                enriched.append(word_obj)
            
            # Небольшая задержка между батчами
            await asyncio.sleep(1)
        
        return enriched
    
    @staticmethod
    async def _call_gpt(words: list[dict]) -> list[dict]:
        """Вызывает GPT для batch обогащения"""
        
        # Фильтруем слова для запроса (не отправляем те что уже полные)
        words_to_enrich = []
        for w in words:
            has_translation = bool(w.get("translation"))
            has_meaning = bool(w.get("meaning"))
            
            if not has_translation or not has_meaning:
                words_to_enrich.append({
                    "word": w["word"],
                    "type": w.get("type"),  # ← передаём тип слова если есть
                    "example": w.get("example"),  # ← передаём пример если есть
                    "needs_translation": not has_translation,
                    "needs_meaning": not has_meaning,
                })
        
        if not words_to_enrich:
            return words
        
        # Создаём запрос для GPT
        request_text = "Дополни данные для следующих слов (JSON формат):\n\n"
        request_text += json.dumps(words_to_enrich, ensure_ascii=False, indent=2)
        request_text += "\n\nОтвети JSON массивом с полями: word, translation (русский перевод), meaning (определение на английском, 1-2 предложения, простой язык)"
        
        system_prompt = """Ты — помощник для обогащения данных словаря английского языка (Oxford 3000).
        
Пользователь присылает JSON с английскими словами и их типами.
Твоя задача — дополнить недостающие данные:
- translation: точный, простой перевод на русский язык
- meaning: определение слова на английском (1-2 простых предложения, легко понимаемые для студентов)

Если в данных есть "example" — используй его для лучшего понимания контекста.

Отвечай ТОЛЬКО валидным JSON массивом в формате:
[
    {"word": "about", "translation": "о, про, около", "meaning": "concerning or dealing with a subject"},
    {"word": "above", "translation": "выше, над", "meaning": "at a higher level or position than something else"},
]

Без пояснений, без markdown, только JSON."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                max_output_tokens=2000
            )
        )
        
        # Парсим ответ
        raw_text = response.text.strip()
        
        # Очищаем от markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text.split("```json")[1]
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("```", 1)[0]
        
        enriched_data = json.loads(raw_text.strip())
        
        # Мержим с оригинальными данными
        for i, original_word in enumerate(words):
            matching = next(
                (e for e in enriched_data if e["word"].lower() == original_word["word"].lower()),
                None
            )
            if matching:
                if not original_word.get("translation"):
                    original_word["translation"] = matching.get("translation")
                if not original_word.get("meaning"):
                    original_word["meaning"] = matching.get("meaning")
        
        return words