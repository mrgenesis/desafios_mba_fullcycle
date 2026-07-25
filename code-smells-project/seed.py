import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = "loja.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            estoque INTEGER,
            categoria TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        )
    """)

    cur.execute("DELETE FROM itens_pedido")
    cur.execute("DELETE FROM pedidos")
    cur.execute("DELETE FROM produtos")
    cur.execute("DELETE FROM usuarios")
    cur.execute(
        "DELETE FROM sqlite_sequence WHERE name IN ('produtos','usuarios','pedidos','itens_pedido')"
    )

    cur.execute(
        "INSERT INTO produtos (id, nome, descricao, preco, estoque, categoria, criado_em) "
        "VALUES (1, 'Produto Seed A', 'Descricao A', 100.00, 50, 'informatica', '2026-01-01 00:00:00')"
    )
    cur.execute(
        "INSERT INTO produtos (id, nome, descricao, preco, estoque, categoria, criado_em) "
        "VALUES (2, 'Produto Seed B', 'Descricao B', 25.50, 5, 'moveis', '2026-01-01 00:00:00')"
    )
    cur.execute(
        "INSERT INTO usuarios (id, nome, email, senha, tipo, criado_em) "
        "VALUES (1, 'Usuario Seed', 'seed@example.com', ?, 'cliente', '2026-01-01 00:00:00')",
        (generate_password_hash("senha123"),),
    )
    cur.execute(
        "INSERT INTO usuarios (id, nome, email, senha, tipo, criado_em) "
        "VALUES (2, 'Admin Seed', 'admin@example.com', ?, 'admin', '2026-01-01 00:00:00')",
        (generate_password_hash("admin123"),),
    )
    cur.execute(
        "INSERT INTO pedidos (id, usuario_id, status, total, criado_em) "
        "VALUES (1, 1, 'pendente', 100.00, '2026-01-01 00:00:00')"
    )
    cur.execute(
        "INSERT INTO itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario) "
        "VALUES (1, 1, 1, 1, 100.00)"
    )

    conn.commit()
    conn.close()
    print("Seed aplicado com sucesso.")


if __name__ == "__main__":
    seed()
