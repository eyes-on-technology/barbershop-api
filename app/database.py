"""
Módulo de conexão com Supabase
"""
from supabase import create_client, Client
from app.config import settings
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SupabaseDB:
    """Classe para gerenciar conexão com Supabase"""

    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

    def health_check(self) -> bool:
        """Verifica se a conexão com Supabase está ok"""
        try:
            response = self.client.table("servicos").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Erro na conexão com Supabase: {e}")
            return False

    # ==================== Clientes ====================
    def get_cliente_by_email(self, email: str) -> Optional[Dict]:
        """Busca cliente por email"""
        try:
            response = (
                self.client.table("clientes")
                .select("*")
                .eq("email", email)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {e}")
            return None

    def get_cliente_by_id(self, cliente_id: str) -> Optional[Dict]:
        """Busca cliente por ID"""
        try:
            response = (
                self.client.table("clientes")
                .select("*")
                .eq("id", cliente_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {e}")
            return None

    def create_cliente(self, cliente_data: Dict) -> Optional[Dict]:
        """Cria novo cliente"""
        try:
            response = (
                self.client.table("clientes")
                .insert(cliente_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            return None

    def update_cliente(self, cliente_id: str, data: Dict) -> Optional[Dict]:
        """Atualiza dados do cliente"""
        try:
            response = (
                self.client.table("clientes")
                .update(data)
                .eq("id", cliente_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            return None

    # ==================== Prestadores ====================
    def get_prestador_by_email(self, email: str) -> Optional[Dict]:
        """Busca prestador por email"""
        try:
            response = (
                self.client.table("prestadores")
                .select("*")
                .eq("email", email)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar prestador: {e}")
            return None

    def get_prestador_by_id(self, prestador_id: str) -> Optional[Dict]:
        """Busca prestador por ID"""
        try:
            response = (
                self.client.table("prestadores")
                .select("*")
                .eq("id", prestador_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar prestador: {e}")
            return None

    def create_prestador(self, prestador_data: Dict) -> Optional[Dict]:
        """Cria novo prestador"""
        try:
            response = (
                self.client.table("prestadores")
                .insert(prestador_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar prestador: {e}")
            return None

    def update_prestador(self, prestador_id: str, data: Dict) -> Optional[Dict]:
        """Atualiza dados do prestador"""
        try:
            response = (
                self.client.table("prestadores")
                .update(data)
                .eq("id", prestador_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar prestador: {e}")
            return None

    def list_prestadores(self, page: int = 1, limit: int = 10) -> tuple[List[Dict], int]:
        """Lista prestadores com paginação"""
        try:
            offset = (page - 1) * limit
            
            # Contar total
            count_response = (
                self.client.table("prestadores")
                .select("id", count="exact")
                .execute()
            )
            total = count_response.count
            
            # Buscar dados
            response = (
                self.client.table("prestadores")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar prestadores: {e}")
            return [], 0

    # ==================== Serviços ====================
    def get_servico_by_id(self, servico_id: str) -> Optional[Dict]:
        """Busca serviço por ID"""
        try:
            response = (
                self.client.table("servicos")
                .select("*")
                .eq("id", servico_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar serviço: {e}")
            return None

    def list_servicos(self, page: int = 1, limit: int = 10, categoria: Optional[str] = None) -> tuple[List[Dict], int]:
        """Lista serviços com paginação e filtro opcional"""
        try:
            offset = (page - 1) * limit
            
            # Contar total
            query = self.client.table("servicos").select("id", count="exact")
            if categoria:
                query = query.eq("categoria", categoria)
            count_response = query.execute()
            total = count_response.count
            
            # Buscar dados
            query = self.client.table("servicos").select("*")
            if categoria:
                query = query.eq("categoria", categoria)
            response = query.range(offset, offset + limit - 1).execute()
            
            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar serviços: {e}")
            return [], 0

    def create_servico(self, servico_data: Dict) -> Optional[Dict]:
        """Cria novo serviço"""
        try:
            response = (
                self.client.table("servicos")
                .insert(servico_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar serviço: {e}")
            return None

    def update_servico(self, servico_id: str, data: Dict) -> Optional[Dict]:
        """Atualiza serviço"""
        try:
            response = (
                self.client.table("servicos")
                .update(data)
                .eq("id", servico_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar serviço: {e}")
            return None

    def delete_servico(self, servico_id: str) -> bool:
        """Deleta serviço"""
        try:
            self.client.table("servicos").delete().eq("id", servico_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar serviço: {e}")
            return False

    # ==================== Disponibilidades ====================
    def list_disponibilidades(
        self,
        prestador_id: str,
        data_inicio: str,
        data_fim: Optional[str] = None,
    ) -> List[Dict]:
        """Lista disponibilidades de um prestador"""
        try:
            query = (
                self.client.table("disponibilidades")
                .select("*")
                .eq("prestador_id", prestador_id)
                .eq("ativo", True)
                .gte("data_hora", data_inicio)
            )
            
            if data_fim:
                query = query.lte("data_hora", data_fim)
            
            response = query.order("data_hora", desc=False).execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao listar disponibilidades: {e}")
            return []

    def create_disponibilidade(self, disponibilidade_data: Dict) -> Optional[Dict]:
        """Cria nova disponibilidade"""
        try:
            response = (
                self.client.table("disponibilidades")
                .insert(disponibilidade_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar disponibilidade: {e}")
            return None

    # ==================== Agendamentos ====================
    def get_agendamento_by_id(self, agendamento_id: str) -> Optional[Dict]:
        """Busca agendamento por ID"""
        try:
            response = (
                self.client.table("agendamentos")
                .select("*")
                .eq("id", agendamento_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar agendamento: {e}")
            return None

    def list_agendamentos_cliente(
        self,
        cliente_id: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Dict], int]:
        """Lista agendamentos do cliente"""
        try:
            offset = (page - 1) * limit
            
            # Contar total
            query = self.client.table("agendamentos").select("id", count="exact").eq("cliente_id", cliente_id)
            if status:
                query = query.eq("status", status)
            count_response = query.execute()
            total = count_response.count
            
            # Buscar dados
            query = (
                self.client.table("agendamentos")
                .select("*")
                .eq("cliente_id", cliente_id)
            )
            if status:
                query = query.eq("status", status)
            response = query.range(offset, offset + limit - 1).order("data_hora", desc=True).execute()
            
            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos do cliente: {e}")
            return [], 0

    def list_agendamentos_prestador(
        self,
        prestador_id: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Dict], int]:
        """Lista agendamentos do prestador"""
        try:
            offset = (page - 1) * limit
            
            # Contar total
            query = self.client.table("agendamentos").select("id", count="exact").eq("prestador_id", prestador_id)
            if status:
                query = query.eq("status", status)
            count_response = query.execute()
            total = count_response.count
            
            # Buscar dados
            query = (
                self.client.table("agendamentos")
                .select("*")
                .eq("prestador_id", prestador_id)
            )
            if status:
                query = query.eq("status", status)
            response = query.range(offset, offset + limit - 1).order("data_hora", desc=True).execute()
            
            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos do prestador: {e}")
            return [], 0

    def create_agendamento(self, agendamento_data: Dict) -> Optional[Dict]:
        """Cria novo agendamento"""
        try:
            response = (
                self.client.table("agendamentos")
                .insert(agendamento_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {e}")
            return None

    def update_agendamento(self, agendamento_id: str, data: Dict) -> Optional[Dict]:
        """Atualiza agendamento"""
        try:
            response = (
                self.client.table("agendamentos")
                .update(data)
                .eq("id", agendamento_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar agendamento: {e}")
            return None

    def count_agendamentos_por_horario(self, data_hora: str, prestador_id: str) -> int:
        """Conta agendamentos para um horário específico"""
        try:
            response = (
                self.client.table("agendamentos")
                .select("id", count="exact")
                .eq("data_hora", data_hora)
                .eq("prestador_id", prestador_id)
                .eq("status", "pendente")
                .execute()
            )
            return response.count
        except Exception as e:
            logger.error(f"Erro ao contar agendamentos: {e}")
            return 0

    def list_agendamentos_admin(
        self,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Dict], int]:
        """Lista todos os agendamentos (admin)"""
        try:
            offset = (page - 1) * limit
            
            # Contar total
            query = self.client.table("agendamentos").select("id", count="exact")
            if status:
                query = query.eq("status", status)
            count_response = query.execute()
            total = count_response.count
            
            # Buscar dados
            query = self.client.table("agendamentos").select("*")
            if status:
                query = query.eq("status", status)
            response = query.range(offset, offset + limit - 1).order("data_hora", desc=True).execute()
            
            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos (admin): {e}")
            return [], 0

    def delete_agendamento(self, agendamento_id: str) -> bool:
        """Deleta agendamento"""
        try:
            self.client.table("agendamentos").delete().eq("id", agendamento_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar agendamento: {e}")
            return False


# Instância global do banco de dados
db = SupabaseDB()