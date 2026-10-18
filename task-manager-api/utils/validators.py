import re
from datetime import datetime

from config.constants import (
    COLOR_LENGTH,
    EMAIL_PATTERN,
    MAX_CATEGORY_DESCRIPTION_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_PAGE_SIZE,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    DUE_DATE_FORMAT,
    TASK_STATUSES,
    USER_ROLES,
)
from middlewares.error_handler import ValidationError


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def require_json_object(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError('Dados inválidos')
    return data


def parse_pagination(args):
    """Optional ?limit=&offset= query parameters (no limit by default)."""
    try:
        limit = int(args['limit']) if args.get('limit') not in (None, '') else None
        offset = int(args['offset']) if args.get('offset') not in (None, '') else 0
    except ValueError:
        raise ValidationError('Parâmetros de paginação inválidos')
    if offset < 0 or (limit is not None and not 0 < limit <= MAX_PAGE_SIZE):
        raise ValidationError(f'limit deve estar entre 1 e {MAX_PAGE_SIZE} e offset deve ser >= 0')
    return limit, offset


def parse_int_param(value, message):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(message)


# --- tasks ----------------------------------------------------------------

def validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def validate_status(status):
    if status not in TASK_STATUSES:
        raise ValidationError('Status inválido')
    return status


def validate_priority(priority):
    if not _is_int(priority):
        raise ValidationError('Prioridade inválida')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return priority


def validate_optional_id(value, message):
    if not value:
        return None
    if not _is_int(value):
        raise ValidationError(message)
    return value


def parse_due_date(value, message):
    if not value:
        return None
    try:
        return datetime.strptime(value, DUE_DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError(message)


def normalize_tags(tags):
    if tags is None or isinstance(tags, str):
        return tags
    if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
        return ','.join(tags)
    raise ValidationError('Tags inválidas')


# --- users ----------------------------------------------------------------

def validate_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValidationError('Nome é obrigatório')
    return name


def validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError('Email inválido')
    return email


def validate_password(password, message):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return password


def validate_role(role):
    if role not in USER_ROLES:
        raise ValidationError('Role inválido')
    return role


def validate_active(active):
    if not isinstance(active, bool):
        raise ValidationError('Campo active deve ser booleano')
    return active


# --- categories -------------------------------------------------------------

def validate_category_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValidationError('Nome é obrigatório')
    if len(name) > MAX_CATEGORY_NAME_LENGTH:
        raise ValidationError('Nome muito longo')
    return name


def validate_category_description(description):
    if description is None:
        return description
    if not isinstance(description, str) or len(description) > MAX_CATEGORY_DESCRIPTION_LENGTH:
        raise ValidationError('Descrição inválida')
    return description


def validate_color(color):
    if not isinstance(color, str) or len(color) != COLOR_LENGTH or color[0] != '#':
        raise ValidationError('Cor inválida')
    return color
