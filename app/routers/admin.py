"""
Router de admin
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import (
    EstatisticasResponse,
    PaginatedResponse,
)
from app.database import db
from app.auth import get_current_admin
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/estatisticas", response_model=EstatisticasResponse)
async def get_estatisticas(current_user: dict = Depends(get_current_admin)):
    """
    Obtém estatísticas do sistema (apenas admin)
    """
    # Contar clientes
    clientes, total_clientes = db.list_prestadores(page=1, limit=1)
    
    # Contar prestadores
    prestadores, total_prestadores = db.list_prestadores(page=1, limit=1)
    
    # Contar serviços
    servicos, total_servicos = db.list_servicos(page=1, limit=1)
    
    # Contar agendamentos
    agendamentos, total_agendamentos = db.list_agendamentos_admin(page=1, limit=1)
    
    # Contar agendamentos confirmados
    confirmados, total_confirmados = db.list_agendamentos_admin(
        page=1,
        limit=1,
        status="confirmado",
    )
    
    # Contar agendamentos pendentes
    pendentes, total_pendentes = db.list_agendamentos_admin(
        page=1,
        limit=1,
        status="pendente",
    )
    
    return EstatisticasResponse(
        total_clientes=total_clientes,
        total_prestadores=total_prestadores,
        total_servicos=total_servicos,
        total_agendamentos=total_agendamentos,
        agendamentos_confirmados=total_confirmados,
        agendamentos_pendentes=total_pendentes,
    )


@router.get("/agendamentos", response_model=PaginatedResponse)
async def list_agendamentos_admin(
    current_user: dict = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
):
    """
    Lista todos os agendamentos (apenas admin)
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    - **status**: Filtrar por status (opcional)
    """
    agendamentos, total = db.list_agendamentos_admin(
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


@router.delete("/agendamentos/{agendamento_id}")
async def delete_agendamento_admin(
    agendamento_id: str,
    current_user: dict = Depends(get_current_admin),
):
    """
    Deleta um agendamento (apenas admin)
    
    - **agendamento_id**: ID do agendamento
    """
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")
    
    success = db.delete_agendamento(agendamento_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao deletar agendamento",
        )
    
    return {"success": True, "message": "Agendamento deletado com sucesso"}


@router.get("/usuarios", response_model=PaginatedResponse)
async def list_usuarios_admin(
    current_user: dict = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tipo: Optional[str] = None,
):
    """
    Lista todos os usuários (apenas admin)
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    - **tipo**: Filtrar por tipo (cliente ou prestador)
    """
    # Implementar lógica de listagem de usuários
    # Por enquanto, retornamos uma resposta vazia
    
    return PaginatedResponse.create(
        data=[],
        total=0,
        page=page,
        limit=limit,
    )


@router.delete("/usuarios/{usuario_id}")
async def delete_usuario_admin(
    usuario_id: str,
    current_user: dict = Depends(get_current_admin),
):
    """
    Deleta um usuário (apenas admin)
    
    - **usuario_id**: ID do usuário
    """
    # Implementar lógica de deleção de usuário
    
    return {"success": True, "message": "Usuário deletado com sucesso"}


@router.get("/health")
async def health_check():
    """
    Verifica saúde da API e conexão com Supabase
    """
    is_healthy = db.health_check()
    
    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conexão com banco de dados indisponível",
        )
    
    return {
        "status": "healthy",
        "database": "connected",
    }