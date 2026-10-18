import re

from config.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from errors import DomainError

EMAIL_PATTERN = re.compile(r"^\S+@\S+\.\S+$")


def require_body(dados):
    if not isinstance(dados, dict) or not dados:
        raise DomainError("Dados inválidos")
    return dados


def require_number(dados, campo, rotulo, minimo=None):
    if campo not in dados:
        raise DomainError(f"{rotulo} é obrigatório")
    valor = dados[campo]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise DomainError(f"{rotulo} deve ser numérico")
    if minimo is not None and valor < minimo:
        raise DomainError(f"{rotulo} não pode ser negativo")
    return valor


def require_integer(dados, campo, rotulo, minimo=None):
    valor = require_number(dados, campo, rotulo, minimo)
    if not isinstance(valor, int):
        raise DomainError(f"{rotulo} deve ser inteiro")
    return valor


def require_text(dados, campo, rotulo):
    if campo not in dados:
        raise DomainError(f"{rotulo} é obrigatório")
    if not isinstance(dados[campo], str):
        raise DomainError(f"{rotulo} deve ser texto")
    return dados[campo]


def optional_number(valor, rotulo):
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise DomainError(f"{rotulo} deve ser numérico")


def parse_pagination(limit, offset):
    try:
        limit = DEFAULT_PAGE_SIZE if limit in (None, "") else int(limit)
        offset = 0 if offset in (None, "") else int(offset)
    except (TypeError, ValueError):
        raise DomainError("limit e offset devem ser inteiros")
    if limit < 1 or offset < 0:
        raise DomainError("limit deve ser >= 1 e offset >= 0")
    return min(limit, MAX_PAGE_SIZE), offset
