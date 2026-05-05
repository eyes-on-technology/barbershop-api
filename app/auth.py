"""
Módulo de autenticação JWT
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.utils.exceptions import InvalidTokenException

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de segurança HTTP Bearer
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Criptografa uma senha"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_expiration_minutes
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica um token JWT"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Dependência para obter usuário autenticado"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: str = payload.get("sub")
    user_type: str = payload.get("type")
    
    if user_id is None:
        raise InvalidTokenException()
    
    return {
        "id": user_id,
        "type": user_type,
        "email": payload.get("email"),
    }


async def get_current_cliente(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependência para obter cliente autenticado"""
    if current_user["type"] != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a clientes",
        )
    return current_user


async def get_current_prestador(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependência para obter prestador autenticado"""
    if current_user["type"] != "prestador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a prestadores",
        )
    return current_user


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependência para obter admin autenticado"""
    # Implementar lógica de verificação de admin no banco de dados
    # Por enquanto, apenas verifica se o usuário está autenticado
    return current_user