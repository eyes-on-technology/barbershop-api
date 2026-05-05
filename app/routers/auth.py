"""
Router de autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.schemas import (
    LoginRequest,
    SignupClienteRequest,
    SignupPrestadorRequest,
    AuthResponse,
)
from app.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import db
from app.utils.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from app.utils.validators import validate_email, validate_password
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Faz login de um usuário
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    """
    email = validate_email(request.email)
    
    # Tentar buscar como cliente
    cliente = db.get_cliente_by_email(email)
    if cliente:
        # Aqui você precisaria buscar a senha do auth.users do Supabase
        # Por enquanto, vamos simular
        user_type = "cliente"
        user_data = cliente
    else:
        # Tentar buscar como prestador
        prestador = db.get_prestador_by_email(email)
        if prestador:
            user_type = "prestador"
            user_data = prestador
        else:
            raise InvalidCredentialsException()
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user_data["id"]),
            "type": user_type,
            "email": user_data["email"],
        },
        expires_delta=access_token_expires,
    )
    
    return AuthResponse(
        token=access_token,
        user={
            "id": str(user_data["id"]),
            "nome": user_data["nome"],
            "email": user_data["email"],
            "telefone": user_data.get("telefone"),
        },
        user_type=user_type,
        expires_in=settings.jwt_expiration_minutes * 60,
    )


@router.post("/signup/cliente", response_model=AuthResponse)
async def signup_cliente(request: SignupClienteRequest):
    """
    Cadastro de novo cliente
    
    - **nome**: Nome completo
    - **email**: Email único
    - **telefone**: Telefone (opcional)
    - **password**: Senha
    """
    email = validate_email(request.email)
    password = validate_password(request.password)
    
    # Verificar se usuário já existe
    if db.get_cliente_by_email(email):
        raise UserAlreadyExistsException()
    
    # Criar cliente
    cliente_data = {
        "nome": request.nome,
        "email": email,
        "telefone": request.telefone,
    }
    
    cliente = db.create_cliente(cliente_data)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar cliente",
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={
            "sub": str(cliente["id"]),
            "type": "cliente",
            "email": cliente["email"],
        },
        expires_delta=access_token_expires,
    )
    
    return AuthResponse(
        token=access_token,
        user={
            "id": str(cliente["id"]),
            "nome": cliente["nome"],
            "email": cliente["email"],
            "telefone": cliente.get("telefone"),
        },
        user_type="cliente",
        expires_in=settings.jwt_expiration_minutes * 60,
    )


@router.post("/signup/prestador", response_model=AuthResponse)
async def signup_prestador(request: SignupPrestadorRequest):
    """
    Cadastro de novo prestador
    
    - **nome**: Nome completo
    - **email**: Email único
    - **telefone**: Telefone (opcional)
    - **especialidade**: Especialidade do prestador
    - **bio**: Bio (opcional)
    - **password**: Senha
    """
    email = validate_email(request.email)
    password = validate_password(request.password)
    
    # Verificar se usuário já existe
    if db.get_prestador_by_email(email):
        raise UserAlreadyExistsException()
    
    # Criar prestador
    prestador_data = {
        "nome": request.nome,
        "email": email,
        "telefone": request.telefone,
        "especialidade": request.especialidade,
        "bio": request.bio,
    }
    
    prestador = db.create_prestador(prestador_data)
    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar prestador",
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={
            "sub": str(prestador["id"]),
            "type": "prestador",
            "email": prestador["email"],
        },
        expires_delta=access_token_expires,
    )
    
    return AuthResponse(
        token=access_token,
        user={
            "id": str(prestador["id"]),
            "nome": prestador["nome"],
            "email": prestador["email"],
            "telefone": prestador.get("telefone"),
            "especialidade": prestador["especialidade"],
        },
        user_type="prestador",
        expires_in=settings.jwt_expiration_minutes * 60,
    )