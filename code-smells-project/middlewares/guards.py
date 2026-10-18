from functools import wraps

from flask import current_app, jsonify


def admin_only(fn):
    """Reject the request with 403 unless admin routes are enabled by configuration."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_app.config.get("ADMIN_ENABLED"):
            return jsonify({"error": "Forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper
