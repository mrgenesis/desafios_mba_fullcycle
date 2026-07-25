from flask import Blueprint, jsonify, request

from controllers import produto_controller

bp = Blueprint("produtos", __name__)


@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = produto_controller.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    resultados = produto_controller.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    produto = produto_controller.buscar_por_id(produto_id)
    return jsonify({"dados": produto, "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    produto_id = produto_controller.criar(dados)
    return jsonify(
        {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}
    ), 201


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados = request.get_json()
    produto_controller.atualizar(produto_id, dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    produto_controller.deletar(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
