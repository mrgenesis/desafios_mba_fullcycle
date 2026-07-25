from flask import Blueprint, jsonify, request

from controllers import usuario_controller

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = usuario_controller.listar()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    usuario = usuario_controller.buscar_por_id(usuario_id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    usuario_id = usuario_controller.criar(dados)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = usuario_controller.login(dados)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
