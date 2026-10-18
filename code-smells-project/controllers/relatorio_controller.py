from config.constants import FAIXAS_DESCONTO
from models import pedido_model


def _calcular_desconto(faturamento):
    for minimo, percentual in FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * percentual
    return 0


def relatorio_vendas():
    resumo = pedido_model.get_resumo_vendas()
    faturamento = resumo["faturamento"]
    pedidos_validos = resumo["pedidos_validos"]
    desconto = _calcular_desconto(faturamento)
    por_status = resumo["por_status"]

    return {
        "total_pedidos": resumo["total_pedidos"],
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": por_status.get("pendente", 0),
        "pedidos_aprovados": por_status.get("aprovado", 0),
        "pedidos_cancelados": por_status.get("cancelado", 0),
        "ticket_medio": round(faturamento / pedidos_validos, 2) if pedidos_validos > 0 else 0,
    }
