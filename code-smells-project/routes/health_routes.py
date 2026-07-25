from flask import Blueprint, jsonify

from config.database import get_db

bp = Blueprint("health", __name__)


@bp.route("/health", methods=["GET"])
def health_check():
    db = get_db()
    produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produtos,
            "usuarios": usuarios,
            "pedidos": pedidos,
        },
        "versao": "1.0.0",
        "ambiente": "producao",
        "db_path": "loja.db",
    }), 200
