"""
Router de disponibilidades — calcula horários livres dinamicamente
"""
from fastapi import APIRouter, Query
from datetime import date, datetime, timedelta
from typing import Optional
from app.database import db
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/disponibilidades", tags=["Disponibilidades"])


@router.get("/horarios-disponiveis")
async def get_horarios_disponiveis(
    prestador_id: Optional[str] = Query(None, description="ID do prestador (opcional se servico_id informado)"),
    servico_id: Optional[str] = Query(None, description="ID do serviço — retorna todos os prestadores disponíveis"),
    data: Optional[date] = Query(None, description="Data específica (YYYY-MM-DD). Se omitida, busca nos próximos X dias"),
    dias: int = Query(30, ge=1, le=60, description="Quantos dias à frente buscar (ignorado se data informada)"),
):
    """
    Retorna horários disponíveis para agendamento.

    - Filtre por **prestador_id** para ver disponibilidade de um prestador específico.
    - Filtre por **servico_id** para ver todos os prestadores que oferecem o serviço e seus horários.
    - Use **data** para consultar um dia específico.
    - Remove: dias inativos, dias bloqueados, horário de almoço e horários com 3+ agendamentos.
    """

    # Resolver lista de prestadores
    if servico_id:
        prestadores = db.list_prestadores_por_servico(servico_id)
        if not prestadores:
            raise NotFoundException("Nenhum prestador encontrado para este serviço")
    elif prestador_id:
        prestador = db.get_prestador_by_id(prestador_id)
        if not prestador:
            raise NotFoundException("Prestador não encontrado")
        prestadores = [prestador]
    else:
        raise NotFoundException("Informe prestador_id ou servico_id")

    horarios_config = db.get_horarios_funcionamento()
    config_por_dia = {h["dia_semana"]: h for h in horarios_config}
    dias_bloqueados = {str(d["data"]) for d in db.get_dias_bloqueados()}

    # Definir intervalo de datas
    if data:
        datas = [data]
    else:
        hoje = date.today()
        datas = [hoje + timedelta(days=i) for i in range(dias)]

    resultado = []

    for prestador in prestadores:
        dias_resultado = []

        for dia in datas:
            dia_semana = dia.weekday() + 1  # 0=segunda → 1, domingo → 0
            if dia_semana == 7:
                dia_semana = 0

            config = config_por_dia.get(dia_semana)
            if not config or not config["ativo"]:
                continue

            if str(dia) in dias_bloqueados:
                continue

            # Gerar horários do dia
            hora_atual = datetime.combine(dia, datetime.strptime(config["hora_inicio"], "%H:%M:%S").time())
            hora_fim = datetime.combine(dia, datetime.strptime(config["hora_fim"], "%H:%M:%S").time())
            almoco_inicio = datetime.combine(dia, datetime.strptime(config["hora_almoco_inicio"], "%H:%M:%S").time())
            almoco_fim = datetime.combine(dia, datetime.strptime(config["hora_almoco_fim"], "%H:%M:%S").time())
            intervalo = timedelta(minutes=config["intervalo_minutos"])

            horarios_dia = []
            while hora_atual < hora_fim:
                # Pular almoço
                if almoco_inicio <= hora_atual < almoco_fim:
                    hora_atual += intervalo
                    continue

                # Não mostrar horários no passado
                if hora_atual > datetime.now():
                    count = db.count_agendamentos_por_horario(hora_atual.isoformat(), prestador["id"])
                    if count < 3:
                        horarios_dia.append({
                            "data_hora": hora_atual.isoformat(),
                            "hora": hora_atual.strftime("%H:%M"),
                            "vagas_disponiveis": 3 - count,
                        })

                hora_atual += intervalo

            if horarios_dia:
                dias_resultado.append({
                    "data": str(dia),
                    "dia_semana": dia.strftime("%A"),
                    "horarios": horarios_dia,
                })

        if dias_resultado:
            resultado.append({
                "prestador_id": prestador["id"],
                "prestador_nome": prestador["nome"],
                "especialidade": prestador.get("especialidade"),
                "dias": dias_resultado,
            })

    return {
        "servico_id": servico_id,
        "prestadores": resultado,
    }