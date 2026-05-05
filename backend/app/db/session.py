from sqlalchemy.ext.asyncio import async_sessionmaker
from .engine import engine

new_session = async_sessionmaker(engine, expire_on_commit=False)