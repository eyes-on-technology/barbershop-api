"""
Router de usuários e perfil
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import (
    ClienteResponse,
    PrestadorResponse,
    PerfilUpdateRequest,
    PaginatedResponse,
)
from app.database import db
from app.auth import get_current_user, get_current_cliente, get_current_prestador
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/perfil/cliente", response_model=ClienteResponse)
async def get_perfil_cliente(current_user: dict = Depends(get_current_cliente)):
    """
    Obtém perfil do cliente autenticado
    """
    cliente = db.get_cliente_by_id(current_user["id"])
    if not cliente:
        raise NotFoundException("Cliente não encontrado")
    
    return ClienteResponse(**cliente)


@router.get("/perfil/prestador", response_model=PrestadorResponse)
async def get_perfil_prestador(current_user: dict = Depends(get_current_prestador)):
    """
    Obtém perfil do prestador autenticado
    """
    prestador = db.get_prestador_by_id(current_user["id"])
    if not prestador:
        raise NotFoundException("Prestador não encontrado")
    
    return PrestadorResponse(**prestador)


@router.put("/perfil/cliente", response_model=ClienteResponse)
async def update_perfil_cliente(
    update: PerfilUpdateRequest,
    current_user: dict = Depends(get_current_cliente),
):
    """
    Atualiza perfil do cliente autenticado
    
    - **nome**: Novo nome (opcional)
    - **telefone**: Novo telefone (opcional)
    """
    update_data = {}
    if update.nome:
        update_data["nome"] = update.nome
    if update.telefone:
        update_data["telefone"] = update.telefone
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar",
        )
    
    cliente_atualizado = db.update_cliente(current_user["id"], update_data)
    if not cliente_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar perfil",
        )
    
    return ClienteResponse(**cliente_atualizado)


@router.put("/perfil/prestador", response_model=PrestadorResponse)
async def update_perfil_prestador(
    update: PerfilUpdateRequest,
    current_user: dict = Depends(get_current_prestador),
):
    """
    Atualiza perfil do prestador autenticado
    
    - **nome**: Novo nome (opcional)
    - **telefone**: Novo telefone (opcional)
    - **especialidade**: Nova especialidade (opcional)
    - **bio**: Nova bio (opcional)
    """
    update_data = {}
    if update.nome:
        update_data["nome"] = update.nome
    if update.telefone:
        update_data["telefone"] = update.telefone
    if update.especialidade:
        update_data["especialidade"] = update.especialidade
    if update.bio:
        update_data["bio"] = update.bio
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar",
        )
    
    prestador_atualizado = db.update_prestador(current_user["id"], update_data)
    if not prestador_atualizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar perfil",
        )
    
    return PrestadorResponse(**prestador_atualizado)


@router.get("/prestadores", response_model=PaginatedResponse)
async def list_prestadores(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Lista todos os prestadores com paginação
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    """
    prestadores, total = db.list_prestadores(page=page, limit=limit)
    
    return PaginatedResponse.create(
        data=[dict(p) for p in prestadores],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/prestadores/{prestador_id}", response_model=PrestadorResponse)
async def get_prestador(prestador_id: str):
    """
    Obtém detalhes de um prestador
    
    - **prestador_id**: ID do prestador
    """
    prestador = db.get_prestador_by_id(prestador_id)
    if not prestador:
        raise NotFoundException("Prestador não encontrado")
    
    return PrestadorResponse(**prestador)


@router.get("/clientes", response_model=PaginatedResponse)
async def list_clientes(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Lista clientes (apenas para admin/prestador)
    
    - **page**: Número da página
    - **limit**: Quantidade por página
    """
    # Aqui você implementaria a lógica de listagem de clientes
    # Por enquanto, retornamos uma resposta vazia
    
    return PaginatedResponse.create(
        data=[],
        total=0,
        page=page,
        limit=limit,
    )