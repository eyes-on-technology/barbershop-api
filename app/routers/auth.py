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

    # Verificar credenciais pelo Supabase Auth
    try:
        auth_response = db.client.auth.sign_in_with_password({
            "email": email,
            "password": request.password,
        })
    except Exception:
        raise InvalidCredentialsException()

    # Buscar dados extras do cliente ou prestador
    cliente = db.get_cliente_by_email(email)
    if cliente:
        user_type = "cliente"
        user_data = cliente
    else:
        prestador = db.get_prestador_by_email(email)
        if prestador:
            user_type = "prestador"
            user_data = prestador
        else:
        # ← ADICIONAR ISSO
            admin = db.get_admin_by_email(email)
            if admin:
                user_type = "admin"
                user_data = admin
            else:
                raise InvalidCredentialsException()
            if prestador:
            # Se for admin, type = "admin", senão "prestador"
                user_type = "admin" if prestador.get("is_admin") else "prestador"
                user_data = prestador
                
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

    # Verificar se já existe
    if db.get_cliente_by_email(email):
        raise UserAlreadyExistsException()

    # 1. Criar no Supabase Auth
    try:
        auth_response = db.client.auth.sign_up({
            "email": email,
            "password": password,
        })
        user_id = auth_response.user.id
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário no Auth")

    # 2. Inserir na tabela clientes com o ID gerado
    cliente_data = {
        "id": user_id,  # ← mesmo ID do Auth
        "nome": request.nome,
        "email": email,
        "telefone": request.telefone,
    }

    cliente = db.create_cliente(cliente_data)
    if not cliente:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    # Criar token JWT próprio
    access_token = create_access_token(
        data={"sub": user_id, "type": "cliente", "email": email},
        expires_delta=timedelta(minutes=settings.jwt_expiration_minutes),
    )

    return AuthResponse(
        token=access_token,
        user={"id": user_id, "nome": cliente["nome"], "email": cliente["email"], "telefone": cliente.get("telefone")},
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

    # 1. Criar no Supabase Auth
    try:
        auth_response = db.client.auth.sign_up({
            "email": email,
            "password": password,
        })
        user_id = auth_response.user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar usuário no Auth",
        )

    # 2. Inserir na tabela prestadores com o ID gerado pelo Auth
    prestador_data = {
        "id": user_id,
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