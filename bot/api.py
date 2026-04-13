# bot/api.py
import aiohttp

BASE_URL = "http://localhost:8000"

async def register_user(telegram_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users", json={"telegram_id": telegram_id}) as r:
            return await r.json()

async def add_word(telegram_id: str, text: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users/{telegram_id}/words", json={"text": text}) as r:
            return await r.json()

async def get_review(telegram_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/users/{telegram_id}/words/review") as r:
            return await r.json()

async def send_review(telegram_id: str, user_word_id: int, result: bool):  # ← bool!
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f"{BASE_URL}/users/{telegram_id}/words/{user_word_id}/review",
            json={"result": result}
        ) as r:
            return await r.json()