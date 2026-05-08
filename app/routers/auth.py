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
    RefreshTokenRequest,
)
from app.auth import (
    create_access_token,
    verify_password,
    get_current_user,
)
from app.database import db
from app.utils.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    InvalidTokenException,
)
from app.utils.validators import validate_email, validate_password
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _build_auth_response(user_data: dict, user_type: str) -> AuthResponse:
    """Helper que monta o AuthResponse padronizado"""
    access_token = create_access_token(
        data={
            "sub": str(user_data["id"]),
            "type": user_type,
            "email": user_data["email"],
        },
        expires_delta=timedelta(minutes=settings.jwt_expiration_minutes),
    )

    user_payload = {
        "id": str(user_data["id"]),
        "nome": user_data["nome"],
        "email": user_data["email"],
        "telefone": user_data.get("telefone"),
    }
    if user_type in ("prestador", "admin"):
        user_payload["especialidade"] = user_data.get("especialidade")

    return AuthResponse(
        token=access_token,
        user=user_payload,
        user_type=user_type,
        expires_in=settings.jwt_expiration_minutes * 60,
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Faz login de um usuário.

    Retorna `user_type` = `cliente` | `prestador` | `admin`
    para o frontend redirecionar para a tela correta.
    """
    email = validate_email(request.email)

    # Verificar credenciais no Supabase Auth
    try:
        db.client.auth.sign_in_with_password({
            "email": email,
            "password": request.password,
        })
    except Exception:
        raise InvalidCredentialsException()

    # Detectar papel: cliente → prestador → admin
    cliente = db.get_cliente_by_email(email)
    if cliente:
        return _build_auth_response(cliente, "cliente")

    prestador = db.get_prestador_by_email(email)
    if prestador:
        user_type = "admin" if prestador.get("is_admin") else "prestador"
        return _build_auth_response(prestador, user_type)

    raise InvalidCredentialsException()


@router.post("/signup/cliente", response_model=AuthResponse)
async def signup_cliente(request: SignupClienteRequest):
    """
    Cadastro de novo cliente.
    """
    email = validate_email(request.email)
    password = validate_password(request.password)

    if db.get_cliente_by_email(email):
        raise UserAlreadyExistsException()

    try:
        auth_response = db.client.auth.sign_up({"email": email, "password": password})
        user_id = auth_response.user.id
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário no Auth")

    cliente = db.create_cliente({
        "id": user_id,
        "nome": request.nome,
        "email": email,
        "telefone": request.telefone,
    })
    if not cliente:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    return _build_auth_response(cliente, "cliente")


@router.post("/signup/prestador", response_model=AuthResponse)
async def signup_prestador(request: SignupPrestadorRequest):
    """
    Cadastro de novo prestador.
    """
    email = validate_email(request.email)
    password = validate_password(request.password)

    if db.get_prestador_by_email(email):
        raise UserAlreadyExistsException()

    try:
        auth_response = db.client.auth.sign_up({"email": email, "password": password})
        user_id = auth_response.user.id
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário no Auth")

    prestador = db.create_prestador({
        "id": user_id,
        "nome": request.nome,
        "email": email,
        "telefone": request.telefone,
        "especialidade": request.especialidade,
        "bio": request.bio,
    })
    if not prestador:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar prestador")

    return _build_auth_response(prestador, "prestador")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Renova o token JWT do usuário autenticado.

    O interceptor do Axios deve chamar este endpoint automaticamente em caso de 401.
    Basta enviar o token atual no header `Authorization: Bearer <token>` — 
    se ainda for válido, retorna um novo token com prazo renovado.
    """
    user_id = current_user["id"]
    user_type = current_user["type"]
    email = current_user["email"]

    # Recarregar dados atualizados do banco
    if user_type == "cliente":
        user_data = db.get_cliente_by_id(user_id)
    else:
        user_data = db.get_prestador_by_id(user_id)

    if not user_data:
        raise InvalidTokenException()

    return _build_auth_response(user_data, user_type)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retorna os dados do usuário autenticado, incluindo seu papel (user_type).
    Útil para o frontend verificar o role sem precisar decodificar o JWT.
    """
    user_id = current_user["id"]
    user_type = current_user["type"]

    if user_type == "cliente":
        user_data = db.get_cliente_by_id(user_id)
    else:
        user_data = db.get_prestador_by_id(user_id)

    if not user_data:
        raise InvalidTokenException()

    return {
        "id": str(user_data["id"]),
        "nome": user_data["nome"],
        "email": user_data["email"],
        "telefone": user_data.get("telefone"),
        "user_type": user_type,
        "especialidade": user_data.get("especialidade") if user_type != "cliente" else None,
        "is_admin": user_data.get("is_admin", False),
    }