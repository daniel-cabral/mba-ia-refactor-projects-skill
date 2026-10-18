import logging

from config.constants import DEFAULT_ROLE
from middlewares.error_handler import ConflictError, NotFoundError, UnauthorizedError, ForbiddenError, ValidationError
from models.task import Task
from models.user import User
from services.auth_service import create_token
from utils.validators import (
    require_json_object,
    validate_active,
    validate_email,
    validate_name,
    validate_password,
    validate_role,
)

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'


def _find_user(user_id):
    user = User.find(user_id)
    if not user:
        raise NotFoundError(USER_NOT_FOUND)
    return user


def list_users(limit=None, offset=0):
    task_counts = Task.counts_by_user()
    result = []
    for user in User.list_all(limit, offset):
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return result


def get_user(user_id):
    user = _find_user(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.for_user(user_id)]
    return data


def create_user(data, allow_privileged=False):
    require_json_object(data)

    if not data.get('name'):
        raise ValidationError('Nome é obrigatório')
    if not data.get('email'):
        raise ValidationError('Email é obrigatório')
    if not data.get('password'):
        raise ValidationError('Senha é obrigatória')

    name = validate_name(data['name'])
    email = validate_email(data['email'])
    password = validate_password(data['password'], 'Senha deve ter no mínimo 4 caracteres')
    if User.find_by_email(email):
        raise ConflictError('Email já cadastrado')

    # Privileged fields are only honoured when explicitly enabled; public requests always create plain users.
    role = validate_role(data.get('role', DEFAULT_ROLE)) if allow_privileged else DEFAULT_ROLE

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save()
    logger.info('User created: %s', user.id)
    return user.to_dict()


def update_user(user_id, data, allow_privileged=False):
    user = _find_user(user_id)
    require_json_object(data)

    if 'name' in data:
        user.name = validate_name(data['name'])
    if 'email' in data:
        email = validate_email(data['email'])
        existing = User.find_by_email(email)
        if existing and existing.id != user_id:
            raise ConflictError('Email já cadastrado')
        user.email = email
    if 'password' in data:
        user.set_password(validate_password(data['password'], 'Senha muito curta'))
    if allow_privileged:
        if 'role' in data:
            user.role = validate_role(data['role'])
        if 'active' in data:
            user.active = validate_active(data['active'])

    user.save()
    return user.to_dict()


def delete_user(user_id):
    _find_user(user_id).delete_with_tasks()
    logger.info('User deleted: %s', user_id)
    return {'message': 'Usuário deletado com sucesso'}


def get_user_tasks(user_id):
    _find_user(user_id)
    result = []
    for task in Task.for_user(user_id):
        data = task.to_summary_dict()
        data['overdue'] = task.is_overdue()
        result.append(data)
    return result


def login(data, secret_key):
    require_json_object(data)

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.find_by_email(email) if isinstance(email, str) else None
    if not user or not isinstance(password, str) or not user.check_password(password):
        logger.warning('Failed login attempt')
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        logger.warning('Login denied for inactive user %s', user.id)
        raise ForbiddenError('Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': create_token(user.id, secret_key),
    }
