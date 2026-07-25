from flask import Blueprint, jsonify

from config.database import get_db
from middlewares.auth import require_admin

bp = Blueprint("admin", __name__)


@bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
