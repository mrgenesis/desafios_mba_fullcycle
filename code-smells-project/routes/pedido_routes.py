from flask import Blueprint, jsonify, request

from controllers import pedido_controller
from middlewares.errors import ApiError

bp = Blueprint("pedidos", __name__)


@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    if not dados:
        raise ApiError({"erro": "Dados inválidos"}, 400)

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ApiError({"erro": "Usuario ID é obrigatório"}, 400)
    if not itens or len(itens) == 0:
        raise ApiError({"erro": "Pedido deve ter pelo menos 1 item"}, 400)

    resultado = pedido_controller.criar(usuario_id, itens)
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    pedidos = pedido_controller.listar_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "")
    pedido_controller.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
