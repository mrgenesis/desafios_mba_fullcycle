import logging

from config.constants import STATUS_PEDIDO_VALIDOS
from middlewares.errors import ApiError
from models import pedido_model, produto_model

logger = logging.getLogger(__name__)


def criar(usuario_id, itens):
    total = 0
    produtos_do_pedido = []

    for item in itens:
        produto = produto_model.get_by_id(item["produto_id"])
        if produto is None:
            raise ApiError(
                {"erro": f"Produto {item['produto_id']} não encontrado", "sucesso": False}, 400
            )
        if produto["estoque"] < item["quantidade"]:
            raise ApiError(
                {"erro": f"Estoque insuficiente para {produto['nome']}", "sucesso": False}, 400
            )
        total += produto["preco"] * item["quantidade"]
        produtos_do_pedido.append((item, produto))

    pedido_id = pedido_model.criar(usuario_id, total)

    for item, produto in produtos_do_pedido:
        pedido_model.adicionar_item(
            pedido_id, item["produto_id"], item["quantidade"], produto["preco"]
        )
        produto_model.decrementar_estoque(item["produto_id"], item["quantidade"])

    pedido_model.commit()

    logger.info("Pedido %s criado para usuario %s", pedido_id, usuario_id)

    return {"pedido_id": pedido_id, "total": total}


def listar_todos():
    return _montar_pedidos(pedido_model.get_all())


def listar_por_usuario(usuario_id):
    return _montar_pedidos(pedido_model.get_by_usuario(usuario_id))


def _montar_pedidos(pedidos):
    ids = [p["id"] for p in pedidos]
    itens_por_pedido = {}
    for item in pedido_model.get_itens(ids):
        itens_por_pedido.setdefault(item["pedido_id"], []).append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return [
        {
            "id": p["id"],
            "usuario_id": p["usuario_id"],
            "status": p["status"],
            "total": p["total"],
            "criado_em": p["criado_em"],
            "itens": itens_por_pedido.get(p["id"], []),
        }
        for p in pedidos
    ]


def atualizar_status(pedido_id, novo_status):
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ApiError({"erro": "Status inválido"}, 400)

    pedido_model.atualizar_status(pedido_id, novo_status)

    if novo_status == "aprovado":
        logger.info("Pedido %s foi aprovado! Preparar envio.", pedido_id)
    if novo_status == "cancelado":
        logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)
