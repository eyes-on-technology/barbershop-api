"""
Router de serviços
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from app.schemas import (
    ServicoCreate,
    ServicoUpdate,
    ServicoResponse,
    PaginatedResponse,
)
from app.database import db, SupabaseDB
from app.auth import get_current_admin
from app.dependencies import get_pagination
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.get("", response_model=PaginatedResponse)
async def list_servicos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    categoria: Optional[str] = None,
):
    """
    Lista todos os serviços com paginação
    
    - **page**: Número da página (padrão: 1)
    - **limit**: Quantidade por página (padrão: 10, máximo: 100)
    - **categoria**: Filtrar por categoria (opcional)
    """
    servicos, total = db.list_servicos(page=page, limit=limit, categoria=categoria)
    
    return PaginatedResponse.create(
        data=[dict(s) for s in servicos],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{servico_id}", response_model=ServicoResponse)
async def get_servico(servico_id: str):
    """
    Obtém detalhes de um serviço específico
    
    - **servico_id**: ID do serviço
    """
    servico = db.get_servico_by_id(servico_id)
    if not servico:
        raise NotFoundException("Serviço não encontrado")
    
    return ServicoResponse(**servico)


@router.post("", response_model=ServicoResponse)
async def create_servico(
    servico: ServicoCreate,
    current_user: dict = Depends(get_current_admin),
):
    """
    Cria novo serviço (apenas admin)
    
    - **nome**: Nome do serviço
    - **descricao**: Descrição (opcional)
    - **preco_base**: Preço base
    - **categoria**: Categoria do serviço
    """
    servico_data = {
        "nome": servico.nome,
        "descricao": servico.descricao,
        "preco_base": servico.preco_base,
        "categoria": servico.categoria,
    }
    
    novo_servico = db.create_servico(servico_data)
    if not novo_servico:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar serviço",
        )
    
    return ServicoResponse(**novo_servico)


@router.put("/{servico_id}", response_model=ServicoResponse)
async def update_servico(
    servico_id: str,
    servico: ServicoUpdate,
    current_user: dict = Depends(get_current_admin),
):
    """
    Atualiza um serviço (apenas admin)
    
    - **servico_id**: ID do serviço
    - **nome**: Novo nome (opcional)
    - **descricao**: Nova descrição (opcional)
    - **preco_base**: Novo preço (opcional)
    - **categoria**: Nova categoria (opcional)
    """
    # Verificar se serviço existe
    if not db.get_servico_by_id(servico_id):
        raise NotFoundException("Serviço não encontrado")
    
    # Preparar dados para atualização
    update_data = {}
    if servico.nome:
        update_data["nome"] = servico.nome
    if servico.descricao:
        update_data["descricao"] = servico.descricao
    if servico.preco_base:
        update_data["preco_base"] = servico.preco_base
    if servico.categoria:
        update_data["categoria"] = servico.categoria
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar",
        )
    
    servico_atualizado = db.update_servico(servico_id, update_data)
    if not servico_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar serviço",
        )
    
    return ServicoResponse(**servico_atualizado)


@router.delete("/{servico_id}")
async def delete_servico(
    servico_id: str,
    current_user: dict = Depends(get_current_admin),
):
    """
    Deleta um serviço (apenas admin)
    
    - **servico_id**: ID do serviço
    """
    # Verificar se serviço existe
    if not db.get_servico_by_id(servico_id):
        raise NotFoundException("Serviço não encontrado")
    
    success = db.delete_servico(servico_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao deletar serviço",
        )
    
    return {"success": True, "message": "Serviço deletado com sucesso"}