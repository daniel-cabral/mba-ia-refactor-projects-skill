from functools import wraps

from flask import current_app

from middlewares.error_handler import ForbiddenError


def admin_only(view):
    """Guard for dangerous routes: forbidden unless ADMIN_ENABLED is set."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_app.config.get('ADMIN_ENABLED'):
            raise ForbiddenError('Forbidden')
        return view(*args, **kwargs)
    return wrapper
