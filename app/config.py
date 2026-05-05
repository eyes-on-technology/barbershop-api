"""
Configurações da aplicação FastAPI
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configurações globais da aplicação"""

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 15

    # Ambiente
    environment: str = "development"
    debug: bool = True

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "https://barbershop-api-evjg.onrender.com",
    ]

    # API
    api_title: str = "Barbershop API"
    api_version: str = "1.0.0"
    api_description: str = "API para gerenciamento de agendamentos de barbearia"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global de configurações
settings = Settings()