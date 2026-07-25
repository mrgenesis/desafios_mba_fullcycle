from config.constants import (
    DESCONTO_FAIXA_1,
    DESCONTO_FAIXA_2,
    DESCONTO_FAIXA_3,
    LIMITE_FAIXA_1,
    LIMITE_FAIXA_2,
    LIMITE_FAIXA_3,
)
from models import relatorio_model


def gerar():
    dados = relatorio_model.contagens()
    faturamento = dados["faturamento"]
    total_pedidos = dados["total_pedidos"]

    desconto = 0
    if faturamento > LIMITE_FAIXA_1:
        desconto = faturamento * DESCONTO_FAIXA_1
    elif faturamento > LIMITE_FAIXA_2:
        desconto = faturamento * DESCONTO_FAIXA_2
    elif faturamento > LIMITE_FAIXA_3:
        desconto = faturamento * DESCONTO_FAIXA_3

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": dados["pendentes"],
        "pedidos_aprovados": dados["aprovados"],
        "pedidos_cancelados": dados["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
