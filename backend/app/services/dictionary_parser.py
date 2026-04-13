import json
import csv
from typing import List, Dict
import asyncio

class DictionaryParser:
    """Парсер различных форматов словарей"""
    
    @staticmethod
    async def parse_json(file_path: str) -> List[Dict]:
        """
        Парсит JSON словарь (универсальный формат)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Определяем формат автоматически
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            
            # Oxford Dictionary формат с "value" ключом
            if "value" in first_item and "word" in first_item["value"]:
                return DictionaryParser._parse_oxford_dict_format(data)
            
            # Обычный массив объектов со словами
            elif "word" in first_item:
                return DictionaryParser._parse_simple_format(data)
        
        # Если это не массив, пробуем парсить как массив на верхнем уровне
        if isinstance(data, dict) and "words" in data:
            return DictionaryParser._parse_simple_format(data["words"])
        
        return data
    
    @staticmethod
    def _parse_oxford_dict_format(data: list) -> List[Dict]:
        """
        Парсит формат Oxford Dictionary API
        {
            "id": 6,
            "value": {
                "word": "about",
                "type": "adverb",
                "level": "A1",
                "examples": [...],
                "phonetics": {...}
            }
        }
        """
        words = []
        
        for item in data:
            if "value" not in item:
                continue
            
            value = item["value"]
            word_obj = {
                "word": value.get("word", "").strip(),
                "type": value.get("type"),  # adverb, noun, verb, etc
                "level": value.get("level"),  # A1, A2, B1, B2, C1, C2
                "phonetics_us": value.get("phonetics", {}).get("us"),
                "phonetics_uk": value.get("phonetics", {}).get("uk"),
                "examples": value.get("examples", []),  # взяли примеры!
            }
            
            # Если есть несколько примеров - берём первый для основного
            if word_obj["examples"]:
                word_obj["example"] = word_obj["examples"][0]
            
            words.append(word_obj)
        
        return words
    
    @staticmethod
    def _parse_simple_format(data: list) -> List[Dict]:
        """
        Парсит простой формат
        [
            {"word": "apple", "example": "...", "translation": "..."},
            ...
        ]
        """
        words = []
        for item in data:
            word_obj = {
                "word": item.get("word", "").strip(),
                "meaning": item.get("meaning"),
                "example": item.get("example"),
                "translation": item.get("translation"),
            }
            if word_obj["word"]:
                words.append(word_obj)
        
        return words
    
    @staticmethod
    async def parse_csv(file_path: str, encoding='utf-8') -> List[Dict]:
        """
        Парсит CSV словарь
        Колонки: word, meaning (опционально), example (опционально), translation (опционально)
        """
        words = []
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                words.append({
                    "word": row["word"].strip(),
                    "type": row.get("type", "").strip() or None,
                    "level": row.get("level", "").strip() or None,
                    "meaning": row.get("meaning", "").strip() or None,
                    "example": row.get("example", "").strip() or None,
                    "translation": row.get("translation", "").strip() or None,
                })
        return words
    
    @staticmethod
    async def parse_plain_text(file_path: str) -> List[Dict]:
        """
        Парсит простой текст (одно слово в строке)
        """
        words = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    words.append({"word": word})
        return words