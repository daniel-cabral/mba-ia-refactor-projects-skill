import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class DomainError(Exception):
    status = 400


class ValidationError(DomainError):
    status = 400


class UnauthorizedError(DomainError):
    status = 401


class ForbiddenError(DomainError):
    status = 403


class NotFoundError(DomainError):
    status = 404


class ConflictError(DomainError):
    status = 409


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(err):
        return jsonify({'error': str(err)}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({'error': err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        logger.exception('Unhandled error')
        return jsonify({'error': 'Internal server error'}), 500
