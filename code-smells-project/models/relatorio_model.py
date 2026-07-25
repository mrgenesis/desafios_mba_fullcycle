from config.database import get_db


def contagens():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0]
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'").fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'").fetchone()[0]
    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento or 0,
        "pendentes": pendentes,
        "aprovados": aprovados,
        "cancelados": cancelados,
    }
