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
    clientes, total_clientes = db.list_clientes(page=1, limit=1)
    prestadores, total_prestadores = db.list_prestadores(page=1, limit=1)
    servicos, total_servicos = db.list_servicos(page=1, limit=1)
    agendamentos, total_agendamentos = db.list_agendamentos_admin(page=1, limit=1)
    confirmados, total_confirmados = db.list_agendamentos_admin(page=1, limit=1, status="confirmado")
    pendentes, total_pendentes = db.list_agendamentos_admin(page=1, limit=1, status="pendente")

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
    agendamentos, total = db.list_agendamentos_admin(page=page, limit=limit, status=status)
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
    agendamento = db.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        raise NotFoundException("Agendamento não encontrado")

    success = db.delete_agendamento(agendamento_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao deletar agendamento")

    return {"success": True, "message": "Agendamento deletado com sucesso"}


@router.get("/usuarios", response_model=PaginatedResponse)
async def list_usuarios_admin(
    current_user: dict = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tipo: Optional[str] = None,
):
    usuarios = []
    total = 0

    if tipo == "cliente":
        clientes, total = db.list_clientes(page=page, limit=limit)
        usuarios = [{"tipo": "cliente", **c} for c in clientes]
    elif tipo == "prestador":
        prestadores, total = db.list_prestadores(page=page, limit=limit)
        usuarios = [{"tipo": "prestador", **p} for p in prestadores]
    else:
        # Retorna ambos
        clientes, total_c = db.list_clientes(page=page, limit=limit)
        prestadores, total_p = db.list_prestadores(page=page, limit=limit)
        usuarios = [{"tipo": "cliente", **c} for c in clientes] + \
                   [{"tipo": "prestador", **p} for p in prestadores]
        total = total_c + total_p

    return PaginatedResponse.create(data=usuarios, total=total, page=page, limit=limit)


@router.delete("/usuarios/{usuario_id}")
async def delete_usuario_admin(
    usuario_id: str,
    tipo: str = Query(..., description="Tipo do usuário: cliente ou prestador"),
    current_user: dict = Depends(get_current_admin),
):
    if tipo == "cliente":
        usuario = db.get_cliente_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Cliente não encontrado")
        db.delete_cliente(usuario_id)
    elif tipo == "prestador":
        usuario = db.get_prestador_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Prestador não encontrado")
        db.delete_prestador(usuario_id)
    else:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'cliente' ou 'prestador'")

    # Deletar também do Supabase Auth
    try:
        db.client.auth.admin.delete_user(usuario_id)
    except Exception:
        pass  # Se falhar no Auth, ignora — já deletou da tabela

    return {"success": True, "message": f"{tipo.capitalize()} deletado com sucesso"}


# ==================== SERVIÇOS (apenas admin) ====================

@router.post("/servicos")
async def create_servico_admin(
    nome: str,
    descricao: Optional[str] = None,
    preco_base: float = 0.0,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_admin),
):
    """Cria um novo serviço (apenas admin)"""
    servico = db.create_servico({
        "nome": nome,
        "descricao": descricao,
        "preco_base": preco_base,
        "categoria": categoria,
    })
    if not servico:
        raise HTTPException(status_code=400, detail="Erro ao criar serviço")
    return {"success": True, "data": servico}


# ==================== DISPONIBILIDADES (apenas admin) ====================

@router.post("/disponibilidades")
async def create_disponibilidade_admin(
    prestador_id: str,
    data_hora: str,
    current_user: dict = Depends(get_current_admin),
):
    """Cria um horário disponível para um prestador (apenas admin)"""
    prestador = db.get_prestador_by_id(prestador_id)
    if not prestador:
        raise NotFoundException("Prestador não encontrado")

    disponibilidade = db.create_disponibilidade({
        "prestador_id": prestador_id,
        "data_hora": data_hora,
        "ativo": True,
    })
    if not disponibilidade:
        raise HTTPException(status_code=400, detail="Erro ao criar disponibilidade")
    return {"success": True, "data": disponibilidade}


@router.get("/health")
async def health_check():
    is_healthy = db.health_check()
    if not is_healthy:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Banco indisponível")
    return {"status": "healthy", "database": "connected"}