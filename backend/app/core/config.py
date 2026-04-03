from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')
    
    DATABASE_URL: str = "sqlite:///./test.db"  # по умолчанию SQLite для тестов
    GEMINI_API_KEY: str = ""  # API ключ для Gemini

settings = Settings()