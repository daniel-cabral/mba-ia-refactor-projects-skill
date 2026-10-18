import logging

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import TIPO_USUARIO_PADRAO
from controllers.validators import EMAIL_PATTERN, parse_pagination, require_body
from errors import ConflictError, DomainError, NotFoundError, UnauthorizedError
from models import usuario_model

logger = logging.getLogger(__name__)


def _texto_obrigatorio(dados, campo):
    valor = dados.get(campo, "")
    return valor if isinstance(valor, str) else ""


def listar(limit=None, offset=None):
    limit, offset = parse_pagination(limit, offset)
    return usuario_model.get_todos_usuarios(limit, offset)


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_usuario_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar(dados):
    dados = require_body(dados)
    nome = _texto_obrigatorio(dados, "nome")
    email = _texto_obrigatorio(dados, "email")
    senha = _texto_obrigatorio(dados, "senha")

    if not nome or not email or not senha:
        raise DomainError("Nome, email e senha são obrigatórios")
    if not EMAIL_PATTERN.match(email):
        raise DomainError("Email inválido")
    if usuario_model.email_existe(email):
        raise ConflictError("Email já cadastrado")

    usuario_id = usuario_model.criar_usuario(nome, email, generate_password_hash(senha), TIPO_USUARIO_PADRAO)
    logger.info("Usuário criado com ID %s", usuario_id)
    return usuario_id


def login(dados):
    dados = require_body(dados) if dados else {}
    email = _texto_obrigatorio(dados, "email")
    senha = _texto_obrigatorio(dados, "senha")

    if not email or not senha:
        raise DomainError("Email e senha são obrigatórios")

    credenciais = usuario_model.get_credenciais_por_email(email)
    if not credenciais or not check_password_hash(credenciais["senha_hash"], senha):
        logger.warning("Login falhou para o usuário informado")
        raise UnauthorizedError("Email ou senha inválidos")

    logger.info("Login bem-sucedido: usuário %s", credenciais["id"])
    return {
        "id": credenciais["id"],
        "nome": credenciais["nome"],
        "email": credenciais["email"],
        "tipo": credenciais["tipo"],
    }
