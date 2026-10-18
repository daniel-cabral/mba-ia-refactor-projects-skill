import logging
import os
import secrets


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    DATABASE_URL = os.environ.get("DATABASE_URL", "loja.db")
    ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "0") == "1"
    ENVIRONMENT = os.environ.get("APP_ENV", "desenvolvimento")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(1024 * 1024)))


if "SECRET_KEY" not in os.environ:
    logging.warning("SECRET_KEY not set; using a random development key")
