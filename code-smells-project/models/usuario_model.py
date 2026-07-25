from config.database import get_db


def get_all():
    db = get_db()
    return db.execute("SELECT * FROM usuarios").fetchall()


def get_by_id(usuario_id):
    db = get_db()
    return db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()


def get_by_email(email):
    db = get_db()
    return db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def create(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cur = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cur.lastrowid


def serialize(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def serialize_login(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
