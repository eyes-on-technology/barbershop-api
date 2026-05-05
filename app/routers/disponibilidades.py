"""
Router de disponibilidades
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import Optional, List
from app.schemas import (
    DisponibilidadeCreate,
    DisponibilidadeResponse,
    PrestadorResponse,
)
from app.database import db
from app.auth import get_current_prestador
from app.utils.exceptions import NotFoundException, ValidationException

router = APIRouter(prefix="/disponibilidades", tags=["Disponibilidades"])


@router.get("/prestador/{prestador_id}")
async def list_disponibilidades_prestador(
    prestador_id: str,
    data_inicio: str = Query(..., description="Data inicial (ISO format)"),
    data_fim: Optional[str] = Query(None, description="Data final (ISO format)"),
):
    """
    Lista disponibilidades de um prestador
    
    - **prestador_id**: ID do prestador
    - **data_inicio**: Data inicial (formato ISO: 2024-01-15T10:00:00)
    - **data_fim**: Data final (opcional)
    """
    # Verificar se prestador existe
    prestador = db.get_prestador_by_id(prestador_id)
    if not prestador:
        raise NotFoundException("Prestador não encontrado")
    
    disponibilidades = db.list_disponibilidades(
        prestador_id=prestador_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    
    return {
        "data": [dict(d) for d in disponibilidades],
        "total": len(disponibilidades),
    }


@router.get("/servico/{servico_id}/horarios")
async def get_horarios_disponiveis(
    servico_id: str,
    data_inicio: str = Query(..., description="Data inicial (ISO format)"),
    data_fim: Optional[str] = Query(None, description="Data final (ISO format)"),
):
    """
    Obtém horários disponíveis para um serviço
    
    - **servico_id**: ID do serviço
    - **data_inicio**: Data inicial
    - **data_fim**: Data final (opcional)
    """
    # Verificar se serviço existe
    servico = db.get_servico_by_id(servico_id)
    if not servico:
        raise NotFoundException("Serviço não encontrado")
    
    # Buscar todos os prestadores que oferecem este serviço
    # Aqui você precisaria implementar uma query na tabela prestador_servicos
    # Por enquanto, retornamos uma resposta vazia
    
    return {
        "servico_id": servico_id,
        "horarios": [],
    }


@router.post("", response_model=DisponibilidadeResponse)
async def create_disponibilidade(
    disponibilidade: DisponibilidadeCreate,
    current_user: dict = Depends(get_current_prestador),
):
    """
    Cria nova disponibilidade (apenas prestador)
    
    - **data_hora**: Data e hora da disponibilidade
    - **ativo**: Se está ativa (padrão: true)
    """
    # Validar se data_hora é no futuro
    try:
        dt = datetime.fromisoformat(str(disponibilidade.data_hora))
        if dt <= datetime.now():
            raise ValidationException("Data e hora devem ser no futuro")
    except ValueError:
        raise ValidationException("Formato de data/hora inválido")
    
    disponibilidade_data = {
        "prestador_id": current_user["id"],
        "data_hora": str(disponibilidade.data_hora),
        "ativo": disponibilidade.ativo,
    }
    
    nova_disponibilidade = db.create_disponibilidade(disponibilidade_data)
    if not nova_disponibilidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar disponibilidade",
        )
    
    return DisponibilidadeResponse(**nova_disponibilidade)


@router.get("/prestador/{prestador_id}/proximas")
async def get_proximas_disponibilidades(
    prestador_id: str,
    limit: int = Query(10, ge=1, le=100),
):
    """
    Obtém próximas disponibilidades de um prestador
    
    - **prestador_id**: ID do prestador
    - **limit**: Quantidade máxima de resultados
    """
    # Verificar se prestador existe
    prestador = db.get_prestador_by_id(prestador_id)
    if not prestador:
        raise NotFoundException("Prestador não encontrado")
    
    # Buscar disponibilidades a partir de agora
    data_inicio = datetime.now().isoformat()
    disponibilidades = db.list_disponibilidades(
        prestador_id=prestador_id,
        data_inicio=data_inicio,
    )
    
    # Limitar resultados
    disponibilidades = disponibilidades[:limit]
    
    return {
        "prestador": PrestadorResponse(**prestador),
        "disponibilidades": [dict(d) for d in disponibilidades],
        "total": len(disponibilidades),
    }