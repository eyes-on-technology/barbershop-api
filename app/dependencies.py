"""
Dependências compartilhadas
"""
from fastapi import Depends
from app.auth import get_current_user, get_current_cliente, get_current_prestador, get_current_admin
from app.database import db
from app.utils.validators import validate_pagination


async def get_db():
    """Dependência para obter instância do banco de dados"""
    return db


async def get_pagination(page: int = 1, limit: int = 10):
    """Dependência para validar parâmetros de paginação"""
    return validate_pagination(page, limit)