"""
Exceções customizadas da aplicação
"""
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Exceção base para erros da API"""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Erro na requisição",
    ):
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedException(APIException):
    """Exceção para erros de autenticação"""

    def __init__(self, detail: str = "Não autorizado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ForbiddenException(APIException):
    """Exceção para erros de permissão"""

    def __init__(self, detail: str = "Acesso proibido"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(APIException):
    """Exceção para recurso não encontrado"""

    def __init__(self, detail: str = "Recurso não encontrado"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(APIException):
    """Exceção para conflito de dados"""

    def __init__(self, detail: str = "Conflito nos dados"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(APIException):
    """Exceção para erro de validação"""

    def __init__(self, detail: str = "Erro de validação"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InvalidCredentialsException(UnauthorizedException):
    """Exceção para credenciais inválidas"""

    def __init__(self):
        super().__init__(detail="Email ou senha inválidos")


class UserAlreadyExistsException(ConflictException):
    """Exceção para usuário já existente"""

    def __init__(self):
        super().__init__(detail="Usuário já existe com este email")


class InvalidTokenException(UnauthorizedException):
    """Exceção para token inválido"""

    def __init__(self):
        super().__init__(detail="Token inválido ou expirado")


class MaxSolicitacoesException(APIException):
    """Exceção para máximo de solicitações atingido"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 3 solicitações por horário já atingido",
        )
