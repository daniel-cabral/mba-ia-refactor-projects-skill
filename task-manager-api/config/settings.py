import logging
import os
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


def _flag(name, default='0'):
    return os.environ.get(name, default) == '1'


def _secret_key():
    key = os.environ.get('SECRET_KEY')
    if not key:
        logger.warning('SECRET_KEY not set; using a random development key')
        key = secrets.token_hex(32)
    return key


class Settings:
    SECRET_KEY = _secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', str(1024 * 1024)))

    DEBUG = _flag('FLASK_DEBUG')
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', '5000'))
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

    CORS_ORIGINS = [o.strip() for o in os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',') if o.strip()]

    # Dangerous routes (account deletion) and privileged fields (role, active) stay closed unless enabled.
    ADMIN_ENABLED = _flag('ADMIN_ENABLED')

    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
