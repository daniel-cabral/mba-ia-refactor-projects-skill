from itsdangerous import URLSafeTimedSerializer

TOKEN_SALT = 'task-manager-auth'


def create_token(user_id, secret_key):
    """Signed, timestamped token (replaces the guessable 'fake-jwt-token-<id>').

    No route verifies tokens yet: authentication is a separate design effort.
    """
    return URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT).dumps({'user_id': user_id})
