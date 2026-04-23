# bot/api.py
import re

import aiohttp

BASE_URL = "http://localhost:8000"

async def register_user(telegram_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users", json={"telegram_id": telegram_id}) as r:
            return await r.json()

async def get_review(telegram_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/users/{telegram_id}/words/review") as r:
            return await r.json()
        
async def get_word(word:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/words/{word}") as r:
            return await r.json()


async def add_word(telegram_id: str, text: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users/{telegram_id}/words", json={"text": text}) as r:
            return await r.json()

def is_valid_word(text: str) -> bool:
    text = text.strip()
    
    # Слишком длинное — это не слово
    if len(text) > 30:
        return False
    
    # Содержит цифры
    if any(c.isdigit() for c in text):
        return False
    
    # Содержит не-буквенные символы (кроме дефиса)
    if not re.match(r'^[a-zA-Z\-]+$', text):
        return False
    
    # Слишком короткое
    if len(text) < 2:
        return False
    
    return True

def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)