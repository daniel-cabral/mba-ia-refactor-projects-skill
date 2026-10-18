from database import get_db


def _produto_para_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_todos_produtos(limit, offset):
    rows = get_db().execute("SELECT * FROM produtos LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return [_produto_para_dict(row) for row in rows]


def get_produto_por_id(produto_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _produto_para_dict(row) if row else None


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def deletar_produto(produto_id):
    db = get_db()
    with db:
        db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def buscar_produtos(termo, categoria, preco_min, preco_max, limit, offset):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)
    query += " LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = get_db().execute(query, params).fetchall()
    return [_produto_para_dict(row) for row in rows]
