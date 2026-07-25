from werkzeug.security import check_password_hash, generate_password_hash

from middlewares.errors import ApiError
from models import usuario_model


def listar():
    return [usuario_model.serialize(u) for u in usuario_model.get_all()]


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if not usuario:
        raise ApiError({"erro": "Usuário não encontrado"}, 404)
    return usuario_model.serialize(usuario)


def criar(dados):
    if not dados:
        raise ApiError({"erro": "Dados inválidos"}, 400)

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ApiError({"erro": "Nome, email e senha são obrigatórios"}, 400)

    senha_hash = generate_password_hash(senha)
    return usuario_model.create(nome, email, senha_hash)


def login(dados):
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ApiError({"erro": "Email e senha são obrigatórios"}, 400)

    usuario = usuario_model.get_by_email(email)
    if usuario and check_password_hash(usuario["senha"], senha):
        return usuario_model.serialize_login(usuario)

    raise ApiError({"erro": "Email ou senha inválidos", "sucesso": False}, 401)
