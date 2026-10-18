import logging

from config.constants import CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from controllers.validators import (
    optional_number,
    parse_pagination,
    require_body,
    require_integer,
    require_number,
    require_text,
)
from errors import DomainError, NotFoundError
from models import produto_model

logger = logging.getLogger(__name__)


def _validar_produto(dados):
    dados = require_body(dados)
    nome = require_text(dados, "nome", "Nome")
    preco = require_number(dados, "preco", "Preço", minimo=0)
    estoque = require_integer(dados, "estoque", "Estoque", minimo=0)
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", "geral")

    if len(nome) < NOME_PRODUTO_MIN:
        raise DomainError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise DomainError("Nome muito longo")
    if not isinstance(descricao, str):
        raise DomainError("Descrição deve ser texto")
    if categoria not in CATEGORIAS_VALIDAS:
        raise DomainError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))
    return nome, descricao, preco, estoque, categoria


def _exigir_produto(produto_id):
    produto = produto_model.get_produto_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return produto


def listar(limit=None, offset=None):
    limit, offset = parse_pagination(limit, offset)
    return produto_model.get_todos_produtos(limit, offset)


def buscar_por_id(produto_id):
    return _exigir_produto(produto_id)


def criar(dados):
    produto_id = produto_model.criar_produto(*_validar_produto(dados))
    logger.info("Produto criado com ID %s", produto_id)
    return produto_id


def atualizar(produto_id, dados):
    _exigir_produto(produto_id)
    produto_model.atualizar_produto(produto_id, *_validar_produto(dados))


def deletar(produto_id):
    _exigir_produto(produto_id)
    produto_model.deletar_produto(produto_id)
    logger.info("Produto %s deletado", produto_id)


def buscar(termo, categoria, preco_min, preco_max, limit=None, offset=None):
    limit, offset = parse_pagination(limit, offset)
    preco_min = optional_number(preco_min, "preco_min")
    preco_max = optional_number(preco_max, "preco_max")
    return produto_model.buscar_produtos(termo, categoria, preco_min, preco_max, limit, offset)
