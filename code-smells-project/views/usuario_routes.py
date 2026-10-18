from flask import Blueprint, jsonify, request

from controllers import usuario_controller

bp = Blueprint("usuarios", __name__)


@bp.get("/usuarios")
def listar_usuarios():
    usuarios = usuario_controller.listar(request.args.get("limit"), request.args.get("offset"))
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@bp.get("/usuarios/<int:usuario_id>")
def buscar_usuario(usuario_id):
    usuario = usuario_controller.buscar_por_id(usuario_id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@bp.post("/usuarios")
def criar_usuario():
    usuario_id = usuario_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@bp.post("/login")
def login():
    usuario = usuario_controller.login(request.get_json(silent=True))
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
