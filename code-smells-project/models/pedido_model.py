from config.constants import STATUS_CANCELADO, STATUS_INICIAL_PEDIDO
from database import get_db
from errors import DomainError, NotFoundError


def _anexar_itens(pedidos):
    """Load the items (with product names) of all given orders in a single query."""
    if not pedidos:
        return pedidos
    por_id = {pedido["id"]: pedido for pedido in pedidos}
    placeholders = ",".join("?" * len(por_id))
    rows = get_db().execute(
        "SELECT ip.pedido_id, ip.produto_id, COALESCE(p.nome, 'Desconhecido') AS produto_nome, "
        "ip.quantidade, ip.preco_unitario "
        "FROM itens_pedido ip LEFT JOIN produtos p ON p.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders}) ORDER BY ip.id",
        list(por_id),
    ).fetchall()
    for row in rows:
        por_id[row["pedido_id"]]["itens"].append({
            "produto_id": row["produto_id"],
            "produto_nome": row["produto_nome"],
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"],
        })
    return pedidos


def _pedidos_para_dicts(rows):
    pedidos = [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        }
        for row in rows
    ]
    return _anexar_itens(pedidos)


def get_pedidos_usuario(usuario_id, limit, offset):
    rows = get_db().execute(
        "SELECT * FROM pedidos WHERE usuario_id = ? LIMIT ? OFFSET ?", (usuario_id, limit, offset)
    ).fetchall()
    return _pedidos_para_dicts(rows)


def get_todos_pedidos(limit, offset):
    rows = get_db().execute("SELECT * FROM pedidos LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return _pedidos_para_dicts(rows)


def get_status_pedido(pedido_id):
    row = get_db().execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    return row["status"] if row else None


def criar_pedido(usuario_id, itens):
    """Create an order with its items and decrement stock atomically."""
    db = get_db()
    with db:
        total = 0
        precos = {}
        for item in itens:
            produto = db.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
            if produto is None:
                raise DomainError(f"Produto {item['produto_id']} não encontrado")
            precos[item["produto_id"]] = produto["preco"]
            total += produto["preco"] * item["quantidade"]

        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_INICIAL_PEDIDO, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            atualizado = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if atualizado.rowcount == 0:
                produto = db.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
                raise DomainError(f"Estoque insuficiente para {produto['nome']}")
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], precos[item["produto_id"]]),
            )
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status_pedido(pedido_id, novo_status):
    """Update the status; a cancellation returns the items to stock in the same transaction."""
    db = get_db()
    with db:
        atualizado = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        if atualizado.rowcount == 0:
            raise NotFoundError("Pedido não encontrado")
        if novo_status == STATUS_CANCELADO:
            db.execute(
                "UPDATE produtos SET estoque = estoque + "
                "(SELECT COALESCE(SUM(quantidade), 0) FROM itens_pedido "
                "WHERE pedido_id = ? AND produto_id = produtos.id) "
                "WHERE id IN (SELECT produto_id FROM itens_pedido WHERE pedido_id = ?)",
                (pedido_id, pedido_id),
            )


def get_resumo_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute(
        "SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE status != ?", (STATUS_CANCELADO,)
    ).fetchone()[0]
    pedidos_validos = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status != ?", (STATUS_CANCELADO,)
    ).fetchone()[0]
    por_status = {
        row["status"]: row["quantidade"]
        for row in db.execute("SELECT status, COUNT(*) AS quantidade FROM pedidos GROUP BY status").fetchall()
    }
    return {
        "total_pedidos": total_pedidos,
        "pedidos_validos": pedidos_validos,
        "faturamento": faturamento,
        "por_status": por_status,
    }
