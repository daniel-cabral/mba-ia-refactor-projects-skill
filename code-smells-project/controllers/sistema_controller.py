import logging
import sqlite3

from config.constants import API_VERSION
from errors import DomainError
from models import sistema_model

logger = logging.getLogger(__name__)


def health(ambiente):
    return {
        "status": "ok",
        "database": "connected",
        "counts": sistema_model.contar_registros(),
        "versao": API_VERSION,
        "ambiente": ambiente,
    }


def resetar_banco():
    sistema_model.resetar_banco()
    logger.warning("Banco de dados resetado")


def executar_query(dados):
    query = dados.get("sql", "") if isinstance(dados, dict) else ""
    if not isinstance(query, str) or not query:
        raise DomainError("Query não informada")
    try:
        return sistema_model.executar_sql(query)
    except sqlite3.Error as erro:
        raise DomainError(str(erro))
