from config.constants import CATEGORIAS_VALIDAS
from middlewares.errors import ApiError
from models import produto_model


def listar():
    return [produto_model.serialize(p) for p in produto_model.get_all()]


def buscar_por_id(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if not produto:
        raise ApiError({"erro": "Produto não encontrado", "sucesso": False}, 404)
    return produto_model.serialize(produto)


def buscar(termo, categoria, preco_min_raw, preco_max_raw):
    preco_min = _parse_float(preco_min_raw, "preco_min")
    preco_max = _parse_float(preco_max_raw, "preco_max")
    produtos = produto_model.search(termo, categoria, preco_min, preco_max)
    return [produto_model.serialize(p) for p in produtos]


def _parse_float(valor, nome_campo):
    if not valor:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ApiError({"erro": f"{nome_campo} inválido"}, 400)


def criar(dados):
    if not dados:
        raise ApiError({"erro": "Dados inválidos"}, 400)
    if "nome" not in dados:
        raise ApiError({"erro": "Nome é obrigatório"}, 400)
    if "preco" not in dados:
        raise ApiError({"erro": "Preço é obrigatório"}, 400)
    if "estoque" not in dados:
        raise ApiError({"erro": "Estoque é obrigatório"}, 400)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ApiError({"erro": "Preço não pode ser negativo"}, 400)
    if estoque < 0:
        raise ApiError({"erro": "Estoque não pode ser negativo"}, 400)
    if len(nome) < 2:
        raise ApiError({"erro": "Nome muito curto"}, 400)
    if len(nome) > 200:
        raise ApiError({"erro": "Nome muito longo"}, 400)
    if categoria not in CATEGORIAS_VALIDAS:
        raise ApiError({"erro": "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)}, 400)

    return produto_model.create(nome, descricao, preco, estoque, categoria)


def atualizar(produto_id, dados):
    existente = produto_model.get_by_id(produto_id)
    if not existente:
        raise ApiError({"erro": "Produto não encontrado"}, 404)

    if not dados:
        raise ApiError({"erro": "Dados inválidos"}, 400)
    if "nome" not in dados:
        raise ApiError({"erro": "Nome é obrigatório"}, 400)
    if "preco" not in dados:
        raise ApiError({"erro": "Preço é obrigatório"}, 400)
    if "estoque" not in dados:
        raise ApiError({"erro": "Estoque é obrigatório"}, 400)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ApiError({"erro": "Preço não pode ser negativo"}, 400)
    if estoque < 0:
        raise ApiError({"erro": "Estoque não pode ser negativo"}, 400)

    produto_model.update(produto_id, nome, descricao, preco, estoque, categoria)


def deletar(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if not produto:
        raise ApiError({"erro": "Produto não encontrado"}, 404)
    produto_model.delete(produto_id)
