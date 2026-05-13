# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    MONGODB_URL: str
    MONGODB_DATABASE_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    ADMIN_SECRET_KEY: str = "chupa-maua"
    # Lê o arquivo .env na raiz do projeto
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instância global para ser importada em outros arquivos
settings = Settings()
