from database import get_db


def contar_registros():
    db = get_db()
    return {
        tabela: db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        for tabela in ("produtos", "usuarios", "pedidos")
    }


def resetar_banco():
    db = get_db()
    with db:
        for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            db.execute(f"DELETE FROM {tabela}")


def executar_sql(query):
    """Run arbitrary SQL. Only reachable through the admin-guarded route."""
    db = get_db()
    with db:
        cursor = db.execute(query)
        if query.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cursor.fetchall()]
    return None
