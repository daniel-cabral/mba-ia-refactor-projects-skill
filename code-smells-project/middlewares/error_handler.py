import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from errors import DomainError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(erro):
        return jsonify({"error": str(erro)}), erro.status

    @app.errorhandler(HTTPException)
    def handle_http_error(erro):
        return jsonify({"error": erro.description}), erro.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(erro):
        logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500
