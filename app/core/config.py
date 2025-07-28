from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "trakr"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    JWT_SECRET_KEY: str = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTc1MzUyNTc3MywiaWF0IjoxNzUzNTI1NzczfQ.fKqCIkRxUwiOJ_9oAU5UvbP7r_I6fxbP86Qax7CQl2Q"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT: str = "5/minute"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings():
    return Settings() 