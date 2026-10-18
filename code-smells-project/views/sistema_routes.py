from flask import Blueprint, current_app, jsonify, request

from config.constants import API_VERSION
from controllers import sistema_controller
from middlewares.guards import admin_only

bp = Blueprint("sistema", __name__)


@bp.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@bp.get("/health")
def health_check():
    return jsonify(sistema_controller.health(current_app.config["ENVIRONMENT"])), 200


@bp.post("/admin/reset-db")
@admin_only
def reset_database():
    sistema_controller.resetar_banco()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


@bp.post("/admin/query")
@admin_only
def executar_query():
    resultado = sistema_controller.executar_query(request.get_json(silent=True))
    if resultado is None:
        return jsonify({"mensagem": "Query executada", "sucesso": True}), 200
    return jsonify({"dados": resultado, "sucesso": True}), 200
