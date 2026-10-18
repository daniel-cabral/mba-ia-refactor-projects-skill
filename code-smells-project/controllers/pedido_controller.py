import logging

from config.constants import STATUS_CANCELADO, STATUS_PEDIDO, TRANSICOES_STATUS
from controllers.validators import parse_pagination, require_body
from errors import ConflictError, DomainError, NotFoundError
from models import pedido_model, usuario_model

logger = logging.getLogger(__name__)


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 1


def _validar_itens(itens):
    if not isinstance(itens, list) or not itens:
        raise DomainError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict) or not _inteiro_positivo(item.get("produto_id")):
            raise DomainError("Cada item deve ter um produto_id válido")
        if not _inteiro_positivo(item.get("quantidade")):
            raise DomainError("Cada item deve ter quantidade inteira maior que zero")
    return itens


def criar(dados):
    dados = require_body(dados)
    usuario_id = dados.get("usuario_id")
    if not usuario_id:
        raise DomainError("Usuario ID é obrigatório")
    if not _inteiro_positivo(usuario_id):
        raise DomainError("Usuario ID inválido")
    itens = _validar_itens(dados.get("itens", []))

    if not usuario_model.get_usuario_por_id(usuario_id):
        raise NotFoundError("Usuário não encontrado")

    resultado = pedido_model.criar_pedido(usuario_id, itens)
    logger.info("Pedido %s criado para o usuário %s", resultado["pedido_id"], usuario_id)
    return resultado


def listar_por_usuario(usuario_id, limit=None, offset=None):
    limit, offset = parse_pagination(limit, offset)
    return pedido_model.get_pedidos_usuario(usuario_id, limit, offset)


def listar_todos(limit=None, offset=None):
    limit, offset = parse_pagination(limit, offset)
    return pedido_model.get_todos_pedidos(limit, offset)


def atualizar_status(pedido_id, dados):
    dados = dados if isinstance(dados, dict) else {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_PEDIDO:
        raise DomainError("Status inválido")

    status_atual = pedido_model.get_status_pedido(pedido_id)
    if status_atual is None:
        raise NotFoundError("Pedido não encontrado")
    if novo_status not in TRANSICOES_STATUS.get(status_atual, []):
        raise ConflictError(f"Transição de status inválida: {status_atual} -> {novo_status}")

    pedido_model.atualizar_status_pedido(pedido_id, novo_status)
    logger.info("Pedido %s: %s -> %s", pedido_id, status_atual, novo_status)
    if novo_status == STATUS_CANCELADO:
        logger.info("Pedido %s cancelado; estoque devolvido", pedido_id)
