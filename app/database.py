"""
Módulo de conexão e operações com o banco de dados Supabase
"""
from typing import Optional, Tuple, List
from supabase import create_client, Client
from app.config import settings


class Database:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )

    def health_check(self) -> bool:
        try:
            self.client.table("servicos").select("id").limit(1).execute()
            return True
        except Exception:
            return False

    # ==================== CLIENTES ====================

    def get_cliente_by_email(self, email: str) -> Optional[dict]:
        try:
            response = self.client.table("clientes").select("*").eq("email", email).single().execute()
            return response.data
        except Exception:
            return None

    def get_cliente_by_id(self, cliente_id: str) -> Optional[dict]:
        try:
            response = self.client.table("clientes").select("*").eq("id", cliente_id).single().execute()
            return response.data
        except Exception:
            return None

    def create_cliente(self, data: dict) -> Optional[dict]:
        response = self.client.table("clientes").insert(data).execute()
        return response.data[0] if response.data else None

    def update_cliente(self, cliente_id: str, data: dict) -> Optional[dict]:
        response = self.client.table("clientes").update(data).eq("id", cliente_id).execute()
        return response.data[0] if response.data else None

    def delete_cliente(self, cliente_id: str) -> bool:
        response = self.client.table("clientes").delete().eq("id", cliente_id).execute()
        return len(response.data) > 0

    def list_clientes(self, page: int = 1, limit: int = 100) -> Tuple[List[dict], int]:
        offset = (page - 1) * limit
        response = self.client.table("clientes").select("*", count="exact").range(offset, offset + limit - 1).execute()
        return response.data or [], response.count or 0

    # ==================== PRESTADORES ====================

    def get_prestador_by_email(self, email: str) -> Optional[dict]:
        try:
            response = self.client.table("prestadores").select("*").eq("email", email).single().execute()
            return response.data
        except Exception:
            return None

    def get_prestador_by_id(self, prestador_id: str) -> Optional[dict]:
        try:
            response = self.client.table("prestadores").select("*").eq("id", prestador_id).single().execute()
            return response.data
        except Exception:
            return None

    def create_prestador(self, data: dict) -> Optional[dict]:
        response = self.client.table("prestadores").insert(data).execute()
        return response.data[0] if response.data else None

    def update_prestador(self, prestador_id: str, data: dict) -> Optional[dict]:
        response = self.client.table("prestadores").update(data).eq("id", prestador_id).execute()
        return response.data[0] if response.data else None

    def delete_prestador(self, prestador_id: str) -> bool:
        response = self.client.table("prestadores").delete().eq("id", prestador_id).execute()
        return len(response.data) > 0

    def list_prestadores(self, page: int = 1, limit: int = 100) -> Tuple[List[dict], int]:
        offset = (page - 1) * limit
        response = self.client.table("prestadores").select("*", count="exact").range(offset, offset + limit - 1).execute()
        return response.data or [], response.count or 0

    # ==================== SERVICOS ====================

    def get_servico_by_id(self, servico_id: str) -> Optional[dict]:
        try:
            response = self.client.table("servicos").select("*").eq("id", servico_id).single().execute()
            return response.data
        except Exception:
            return None

    def list_servicos(self, page: int = 1, limit: int = 100, categoria: Optional[str] = None) -> Tuple[List[dict], int]:
        offset = (page - 1) * limit
        query = self.client.table("servicos").select("*", count="exact")
        if categoria:
            query = query.eq("categoria", categoria)
        response = query.range(offset, offset + limit - 1).execute()
        return response.data or [], response.count or 0

    def create_servico(self, data: dict) -> Optional[dict]:
        try:
            response = self.client.table("servicos").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao criar serviço: {e}")
            return None

    def update_servico(self, servico_id: str, data: dict) -> Optional[dict]:
        response = self.client.table("servicos").update(data).eq("id", servico_id).execute()
        return response.data[0] if response.data else None

    def delete_servico(self, servico_id: str) -> bool:
        response = self.client.table("servicos").delete().eq("id", servico_id).execute()
        return len(response.data) > 0

    # ==================== AGENDAMENTOS ====================

    def create_agendamento(self, data: dict) -> Optional[dict]:
        response = self.client.table("agendamentos").insert(data).execute()
        return response.data[0] if response.data else None

    def get_agendamento_by_id(self, agendamento_id: str) -> Optional[dict]:
        try:
            response = self.client.table("agendamentos").select("*").eq("id", agendamento_id).single().execute()
            return response.data
        except Exception:
            return None

    def list_agendamentos_by_cliente(self, cliente_id: str) -> list:
        response = self.client.table("agendamentos").select("*").eq("cliente_id", cliente_id).execute()
        return response.data or []

    def list_agendamentos_by_prestador(self, prestador_id: str) -> list:
        response = self.client.table("agendamentos").select("*").eq("prestador_id", prestador_id).execute()
        return response.data or []

    def list_agendamentos_admin(self, page: int = 1, limit: int = 100, status: Optional[str] = None) -> Tuple[List[dict], int]:
        offset = (page - 1) * limit
        query = self.client.table("agendamentos").select("*", count="exact")
        if status:
            query = query.eq("status", status)
        response = query.range(offset, offset + limit - 1).execute()
        return response.data or [], response.count or 0

    def update_agendamento(self, agendamento_id: str, data: dict) -> Optional[dict]:
        response = self.client.table("agendamentos").update(data).eq("id", agendamento_id).execute()
        return response.data[0] if response.data else None

    def delete_agendamento(self, agendamento_id: str) -> bool:
        response = self.client.table("agendamentos").delete().eq("id", agendamento_id).execute()
        return len(response.data) > 0

    # ==================== DISPONIBILIDADES ====================

    def create_disponibilidade(self, data: dict) -> Optional[dict]:
        response = self.client.table("disponibilidades").insert(data).execute()
        return response.data[0] if response.data else None

    def list_disponibilidades_by_prestador(self, prestador_id: str) -> list:
        response = self.client.table("disponibilidades").select("*").eq("prestador_id", prestador_id).execute()
        return response.data or []

    def delete_disponibilidade(self, disponibilidade_id: str) -> bool:
        response = self.client.table("disponibilidades").delete().eq("id", disponibilidade_id).execute()
        return len(response.data) > 0

    # ==================== HORARIOS FUNCIONAMENTO ====================

def get_horarios_funcionamento(self) -> list:
    response = self.client.table("horarios_funcionamento").select("*").order("dia_semana").execute()
    return response.data or []

def update_horario_funcionamento(self, dia_semana: int, data: dict) -> Optional[dict]:
    response = self.client.table("horarios_funcionamento").update(data).eq("dia_semana", dia_semana).execute()
    return response.data[0] if response.data else None

# ==================== DIAS BLOQUEADOS ====================

def get_dias_bloqueados(self) -> list:
    response = self.client.table("dias_bloqueados").select("*").order("data").execute()
    return response.data or []

def create_dia_bloqueado(self, data: dict) -> Optional[dict]:
    try:
        response = self.client.table("dias_bloqueados").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None

def delete_dia_bloqueado(self, data: str) -> bool:
    response = self.client.table("dias_bloqueados").delete().eq("data", data).execute()
    return len(response.data) > 0

# ==================== AGENDAMENTOS - métodos que faltam ====================

def count_agendamentos_por_horario(self, data_hora: str, prestador_id: str) -> int:
    response = (
        self.client.table("agendamentos")
        .select("id", count="exact")
        .eq("data_hora", data_hora)
        .eq("prestador_id", prestador_id)
        .in_("status", ["pendente", "confirmado"])
        .execute()
    )
    return response.count or 0

def list_agendamentos_cliente(self, cliente_id: str, page: int = 1, limit: int = 10, status: Optional[str] = None):
    offset = (page - 1) * limit
    query = self.client.table("agendamentos").select("*", count="exact").eq("cliente_id", cliente_id)
    if status:
        query = query.eq("status", status)
    response = query.range(offset, offset + limit - 1).execute()
    return response.data or [], response.count or 0

def list_agendamentos_prestador(self, prestador_id: str, page: int = 1, limit: int = 10, status: Optional[str] = None):
    offset = (page - 1) * limit
    query = self.client.table("agendamentos").select("*", count="exact").eq("prestador_id", prestador_id)
    if status:
        query = query.eq("status", status)
    response = query.range(offset, offset + limit - 1).execute()
    return response.data or [], response.count or 0

db = Database()