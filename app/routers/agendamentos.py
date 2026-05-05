"""
Router de agendamentos com lógica de negócio
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import (
    AgendamentoCreate,
    AgendamentoResponse,
    AgendamentoUpdateStatus,
    PaginatedResponse,
    SolicitacaoResponse,
    SolicitacaoAcaoRequest,
)
from app.database import db
from app.auth import get_current_user, get_current_cliente, get_current_prestador
from app.utils.exceptions import (
    NotFoundException,
    MaxSolicitacoesException,
    ValidationException,
)

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])

# Constante: máximo de solicitações por horário
MAX_SOLICITACOES_POR_HORARIO = 3


@router.post("", response_model=AgendamentoResponse)
async def create_agendamento(
    agendamento: AgendamentoCreate,
    current_user: dict = Depends(get_current_cliente),
):
    """
    Cria novo agendamento (apenas cliente)
    
    Lógica de negócio:
    - Máximo 3 solicitações por horário e prestador
    - Data/hora deve ser no futuro
    - Prestador e serviço devem existir
    
    - **prestador_id**: ID do prestador
    - **servico_id**: ID do serviço
    - **data_hora**: Data e hora do agendamento
    """
    # Verificar se prestador existe
    prestador = db.get_prestador_by_id(agendamento.prestador_id)
    if not prestador:
        raise NotFoundException("Prestador não encontrado")
    
    # Verificar se serviço existe
    servico = db.get_servico_by_id(agendamento.servico_id)
    if not servico:
        raise NotFoundException("Serviço não encontrado")
    
    # Verificar limite de solicitações por horário
    count = db.count_agendamentos_por_horario(
        str(agendamento.data_hora),
        agendamento.prestador_id,
    )
    
    if count >= MAX_SOLICITACOES_POR_HORARIO:
        raise MaxSolicitacoesException()
    
    # Criar agendamento
    agendamento_data = {
        "cliente_id": current_user["id"],
        "prestador_id": agendamento.prestador_id,
        "servico_id": agendamento.servico_id,
        "data_hora": str(agendamento.data_hora),
        "status": "pendente",
    }
    
    novo_agendamento = db.create_agendamento(agendamento_data)
    if not novo_agendamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar agendamento",
        )
    
    return AgendamentoResponse(**novo_agendamento)


@router.get("/cliente", response_model=PaginatedResponse)
async def list_agendamentos_cliente(
    current_user: dict = Depends(get_current_cliente),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
):
    """
    Lista agendamentos do cliente autenticado
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    - **status**: Filtrar por status (pendente, confirmado, cancelado, concluido)
    """
    agendamentos, total = db.list_agendamentos_cliente(
        cliente_id=current_user["id"],
        page=page,
        limit=limit,
        status=status,
    )
    
    return PaginatedResponse.create(
        data=[dict(a) for a in agendamentos],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/prestador", response_model=PaginatedResponse)
async def list_agendamentos_prestador(
    current_user: dict = Depends(get_current_prestador),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
):
    """
    Lista agendamentos do prestador autenticado
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    - **status**: Filtrar por status
    """
    agendamentos, total = db.list_agendamentos_prestador(
        prestador_id=current_user["id"],
        page=page,
        limit=limit,
        status=status,
    )
    
    return PaginatedResponse.create(
        data=[dict(a) for a in agendamentos],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{agendamento_id}", response_model=AgendamentoResponse)
async def get_agendamento(
    agendamento_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Obtém detalhes de um agendamento
    
    - **agendamento_id**: ID do agendamento
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    # Verificar permissão (cliente ou prestador do agendamento)
    if (
        agendamento["cliente_id"] != current_user["id"]
        and agendamento["prestador_id"] != current_user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )
    
    return AgendamentoResponse(**agendamento)


@router.put("/{agendamento_id}/status", response_model=AgendamentoResponse)
async def update_agendamento_status(
    agendamento_id: str,
    update: AgendamentoUpdateStatus,
    current_user: dict = Depends(get_current_prestador),
):
    """
    Atualiza status do agendamento (apenas prestador)
    
    - **agendamento_id**: ID do agendamento
    - **status**: Novo status (confirmado, cancelado, concluido)
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    # Verificar se é o prestador do agendamento
    if agendamento["prestador_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o prestador pode atualizar o status",
        )
    
    agendamento_atualizado = db.update_agendamento(
        agendamento_id,
        {"status": update.status},
    )
    
    if not agendamento_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar agendamento",
        )
    
    return AgendamentoResponse(**agendamento_atualizado)


@router.put("/{agendamento_id}/cancelar")
async def cancelar_agendamento(
    agendamento_id: str,
    current_user: dict = Depends(get_current_cliente),
):
    """
    Cancela um agendamento (apenas cliente)
    
    - **agendamento_id**: ID do agendamento
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    # Verificar se é o cliente do agendamento
    if agendamento["cliente_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o cliente pode cancelar",
        )
    
    # Verificar se pode cancelar (apenas pendente)
    if agendamento["status"] != "pendente":
        raise ValidationException("Apenas agendamentos pendentes podem ser cancelados")
    
    agendamento_atualizado = db.update_agendamento(
        agendamento_id,
        {"status": "cancelado"},
    )
    
    if not agendamento_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao cancelar agendamento",
        )
    
    return {"success": True, "message": "Agendamento cancelado com sucesso"}


@router.get("/solicitacoes/pendentes", response_model=list)
async def get_solicitacoes_pendentes(
    current_user: dict = Depends(get_current_prestador),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Lista solicitações pendentes do prestador
    
    Retorna agendamentos com status "pendente"
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    """
    agendamentos, total = db.list_agendamentos_prestador(
        prestador_id=current_user["id"],
        page=page,
        limit=limit,
        status="pendente",
    )
    
    return {
        "data": [dict(a) for a in agendamentos],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.put("/solicitacoes/{agendamento_id}/aprovar")
async def aprovar_solicitacao(
    agendamento_id: str,
    current_user: dict = Depends(get_current_prestador),
):
    """
    Aprova uma solicitação de agendamento (apenas prestador)
    
    - **agendamento_id**: ID do agendamento
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    # Verificar se é o prestador
    if agendamento["prestador_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o prestador pode aprovar",
        )
    
    # Verificar se está pendente
    if agendamento["status"] != "pendente":
        raise ValidationException("Apenas solicitações pendentes podem ser aprovadas")
    
    agendamento_atualizado = db.update_agendamento(
        agendamento_id,
        {"status": "confirmado"},
    )
    
    if not agendamento_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao aprovar solicitação",
        )
    
    return {"success": True, "message": "Solicitação aprovada com sucesso"}


@router.put("/solicitacoes/{agendamento_id}/rejeitar")
async def rejeitar_solicitacao(
    agendamento_id: str,
    request: SolicitacaoAcaoRequest,
    current_user: dict = Depends(get_current_prestador),
):
    """
    Rejeita uma solicitação de agendamento (apenas prestador)
    
    - **agendamento_id**: ID do agendamento
    - **motivo**: Motivo da rejeição (opcional)
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    # Verificar se é o prestador
    if agendamento["prestador_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o prestador pode rejeitar",
        )
    
    # Verificar se está pendente
    if agendamento["status"] != "pendente":
        raise ValidationException("Apenas solicitações pendentes podem ser rejeitadas")
    
    agendamento_atualizado = db.update_agendamento(
        agendamento_id,
        {"status": "cancelado"},
    )
    
    if not agendamento_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao rejeitar solicitação",
        )
    
    return {"success": True, "message": "Solicitação rejeitada com sucesso"}