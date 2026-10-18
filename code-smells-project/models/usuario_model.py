from database import get_db


def _usuario_para_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_todos_usuarios(limit, offset):
    rows = get_db().execute("SELECT * FROM usuarios LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return [_usuario_para_dict(row) for row in rows]


def get_usuario_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _usuario_para_dict(row) if row else None


def get_credenciais_por_email(email):
    """Return the user fields plus the password hash, for login verification only."""
    row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "senha_hash": row["senha"],
    }


def email_existe(email):
    return get_db().execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone() is not None


def criar_usuario(nome, email, senha_hash, tipo):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
    return cursor.lastrowid
