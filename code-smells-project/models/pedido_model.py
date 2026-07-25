from config.database import get_db


def criar(usuario_id, total):
    db = get_db()
    cur = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    return cur.lastrowid


def adicionar_item(pedido_id, produto_id, quantidade, preco_unitario):
    db = get_db()
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def commit():
    get_db().commit()


def get_all():
    db = get_db()
    return db.execute("SELECT * FROM pedidos").fetchall()


def get_by_usuario(usuario_id):
    db = get_db()
    return db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()


def get_itens(pedido_ids):
    if not pedido_ids:
        return []
    db = get_db()
    placeholders = ",".join("?" for _ in pedido_ids)
    query = f"""
        SELECT itens_pedido.pedido_id, itens_pedido.produto_id, itens_pedido.quantidade,
               itens_pedido.preco_unitario,
               COALESCE(produtos.nome, 'Desconhecido') AS produto_nome
        FROM itens_pedido
        LEFT JOIN produtos ON produtos.id = itens_pedido.produto_id
        WHERE itens_pedido.pedido_id IN ({placeholders})
    """
    return db.execute(query, pedido_ids).fetchall()


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
