import asyncio
import sys
import json
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.dictionary_parser import DictionaryParser
from app.services.word_enricher import WordEnricher
from app.repositories.WordRepository import WordRepository
from app.core.database import create_tables

async def main():
    print("📚 Загружаю Oxford 3000 словарь...\n")
    
    # 1. Создаём таблицы если их нет
    await create_tables()
    print("✅ Таблицы БД готовы\n")
    
    # 2. Парсим словарь
    dictionary_file = Path(__file__).parent / "full-word.json"
    
    if not dictionary_file.exists():
        print(f"❌ Файл {dictionary_file} не найден!")
        print("   Положи сюда Oxford Dictionary JSON файл")
        return
    
    # Парсим (формат определяется автоматически)
    words = await DictionaryParser.parse_json(str(dictionary_file))
    
    print(f"✅ Прочитал {len(words)} слов\n")
    
    # 3. Фильтруем пустые слова
    words = [w for w in words if w.get("word")]
    print(f"✅ После фильтрации: {len(words)} слов\n")
    
    # 4. Обогащаем данные через GPT (если нет переводов/meanings)
    print("🤖 Генерирую переводы и meanings через GPT...")
    words = await WordEnricher.enrich_words(words, batch_size=15)
    print("✅ Данные обогащены\n")
    
    # 5. Подготавливаем для БД
    valid_words = []
    for w in words:
        if w.get("word") and w.get("translation"):
            word_for_db = {
                "word": w["word"],
                "translation": w["translation"],
                "meaning": w.get("meaning"),
                "example": w.get("example"),
            }
            valid_words.append(word_for_db)
    
    print(f"💾 Готовых слов для загрузки: {len(valid_words)} из {len(words)}\n")
    
    # 6. Загружаем в БД батчами
    print("💾 Загружаю в БД...")
    
    for i in range(0, len(valid_words), 50):
        batch = valid_words[i:i + 50]
        await WordRepository.bulk_create(batch)
        print(f"   ✅ Загружено {min(i + 50, len(valid_words))}/{len(valid_words)}")
    
    print("\n✨ Готово! Oxford 3000 загружены в БД")

if __name__ == "__main__":
    asyncio.run(main())