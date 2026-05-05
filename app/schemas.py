"""
Schemas Pydantic para requisições e respostas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== Enums ====================
class UserType(str, Enum):
    """Tipos de usuário"""
    CLIENTE = "cliente"
    PRESTADOR = "prestador"


class AgendamentoStatus(str, Enum):
    """Status do agendamento"""
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    CONCLUIDO = "concluido"


# ==================== Auth ====================
class LoginRequest(BaseModel):
    """Requisição de login"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignupClienteRequest(BaseModel):
    """Requisição de cadastro de cliente"""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefone: Optional[str] = None
    password: str = Field(..., min_length=6)


class SignupPrestadorRequest(BaseModel):
    """Requisição de cadastro de prestador"""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefone: Optional[str] = None
    especialidade: str = Field(..., min_length=3, max_length=100)
    bio: Optional[str] = None
    password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    """Resposta de autenticação"""
    token: str
    user: dict
    user_type: UserType
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Requisição para renovar token"""
    refresh_token: str


# ==================== Usuários ====================
class ClienteBase(BaseModel):
    """Base para cliente"""
    nome: str
    email: str
    telefone: Optional[str] = None


class ClienteResponse(ClienteBase):
    """Resposta de cliente"""
    id: str
    criado_em: datetime

    class Config:
        from_attributes = True


class PrestadorBase(BaseModel):
    """Base para prestador"""
    nome: str
    email: str
    telefone: Optional[str] = None
    especialidade: str
    bio: Optional[str] = None


class PrestadorResponse(PrestadorBase):
    """Resposta de prestador"""
    id: str
    criado_em: datetime

    class Config:
        from_attributes = True


class PerfilUpdateRequest(BaseModel):
    """Requisição para atualizar perfil"""
    nome: Optional[str] = None
    telefone: Optional[str] = None
    especialidade: Optional[str] = None
    bio: Optional[str] = None


# ==================== Serviços ====================
class ServicoBase(BaseModel):
    """Base para serviço"""
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    preco_base: float = Field(..., gt=0)
    categoria: str = Field(..., min_length=3, max_length=50)


class ServicoCreate(ServicoBase):
    """Requisição para criar serviço"""
    pass


class ServicoUpdate(BaseModel):
    """Requisição para atualizar serviço"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco_base: Optional[float] = None
    categoria: Optional[str] = None


class ServicoResponse(ServicoBase):
    """Resposta de serviço"""
    id: str

    class Config:
        from_attributes = True


# ==================== Disponibilidades ====================
class DisponibilidadeBase(BaseModel):
    """Base para disponibilidade"""
    data_hora: datetime
    ativo: bool = True


class DisponibilidadeCreate(DisponibilidadeBase):
    """Requisição para criar disponibilidade"""
    pass


class DisponibilidadeResponse(DisponibilidadeBase):
    """Resposta de disponibilidade"""
    id: str
    prestador_id: str

    class Config:
        from_attributes = True


# ==================== Agendamentos ====================
class AgendamentoBase(BaseModel):
    """Base para agendamento"""
    cliente_id: str
    prestador_id: str
    servico_id: str
    data_hora: datetime
    status: AgendamentoStatus = AgendamentoStatus.PENDENTE


class AgendamentoCreate(BaseModel):
    """Requisição para criar agendamento"""
    prestador_id: str
    servico_id: str
    data_hora: datetime


class AgendamentoResponse(AgendamentoBase):
    """Resposta de agendamento"""
    id: str
    cliente: Optional[ClienteResponse] = None
    prestador: Optional[PrestadorResponse] = None
    servico: Optional[ServicoResponse] = None

    class Config:
        from_attributes = True


class AgendamentoUpdateStatus(BaseModel):
    """Requisição para atualizar status do agendamento"""
    status: AgendamentoStatus


# ==================== Solicitações ====================
class SolicitacaoResponse(BaseModel):
    """Resposta de solicitação"""
    id: str
    agendamento_id: str
    cliente_id: str
    prestador_id: str
    servico_id: str
    data_hora: datetime
    status: str
    cliente: Optional[ClienteResponse] = None
    prestador: Optional[PrestadorResponse] = None
    servico: Optional[ServicoResponse] = None

    class Config:
        from_attributes = True


class SolicitacaoAcaoRequest(BaseModel):
    """Requisição para aprovar/rejeitar solicitação"""
    motivo: Optional[str] = None


# ==================== Paginação ====================
class PaginatedResponse(BaseModel):
    """Resposta paginada genérica"""
    data: List[dict]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def create(cls, data: List[dict], total: int, page: int, limit: int):
        """Factory method para criar resposta paginada"""
        pages = (total + limit - 1) // limit  # Arredonda para cima
        return cls(data=data, total=total, page=page, limit=limit, pages=pages)


# ==================== Admin ====================
class EstatisticasResponse(BaseModel):
    """Resposta de estatísticas"""
    total_clientes: int
    total_prestadores: int
    total_servicos: int
    total_agendamentos: int
    agendamentos_confirmados: int
    agendamentos_pendentes: int


class UsuarioListResponse(BaseModel):
    """Resposta para listagem de usuários"""
    id: str
    nome: str
    email: str
    tipo: UserType
    criado_em: datetime

    class Config:
        from_attributes = True


# ==================== Respostas Genéricas ====================
class SuccessResponse(BaseModel):
    """Resposta de sucesso genérica"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Resposta de erro genérica"""
    success: bool = False
    message: str
    error: Optional[str] = None