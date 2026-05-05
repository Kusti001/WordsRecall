import asyncio
import sys
from pathlib import Path

# Добавляем backend директорию в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.db.init_db import User, engine, Model

async def recreate_users_table():
    async with engine.begin() as conn:
        # Удаляем старую таблицу
        await conn.run_sync(User.__table__.drop, checkfirst=True)
        # Создаём новую
        await conn.run_sync(User.__table__.create)
        print("✅ Таблица users пересоздана!")

asyncio.run(recreate_users_table())