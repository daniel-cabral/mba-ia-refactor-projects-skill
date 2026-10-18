import logging

from config.constants import DEFAULT_PRIORITY, DEFAULT_TASK_STATUS
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utc_now
from utils.validators import (
    normalize_tags,
    parse_due_date,
    parse_int_param,
    require_json_object,
    validate_optional_id,
    validate_priority,
    validate_status,
    validate_title,
)

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'


def _find_task(task_id):
    task = Task.find(task_id)
    if not task:
        raise NotFoundError(TASK_NOT_FOUND)
    return task


def _ensure_user_exists(user_id):
    if user_id is not None and not User.find(user_id):
        raise NotFoundError('Usuário não encontrado')


def _ensure_category_exists(category_id):
    if category_id is not None and not Category.find(category_id):
        raise NotFoundError('Categoria não encontrada')


def _with_overdue(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def list_tasks(limit=None, offset=0):
    result = []
    for task in Task.list_with_relations(limit, offset):
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return result


def get_task(task_id):
    return _with_overdue(_find_task(task_id))


def create_task(data):
    require_json_object(data)

    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')
    validate_title(title)

    status = validate_status(data.get('status', DEFAULT_TASK_STATUS))
    priority = validate_priority(data.get('priority', DEFAULT_PRIORITY))
    user_id = validate_optional_id(data.get('user_id'), 'user_id inválido')
    category_id = validate_optional_id(data.get('category_id'), 'category_id inválido')
    _ensure_user_exists(user_id)
    _ensure_category_exists(category_id)

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
        due_date=parse_due_date(data.get('due_date'), 'Formato de data inválido. Use YYYY-MM-DD'),
        tags=normalize_tags(data.get('tags')) or None,
    )
    task.save()
    logger.info('Task created: %s', task.id)
    return task.to_dict()


def update_task(task_id, data):
    task = _find_task(task_id)
    require_json_object(data)

    if 'title' in data:
        task.title = validate_title(data['title'])
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = validate_status(data['status'])
    if 'priority' in data:
        task.priority = validate_priority(data['priority'])
    if 'user_id' in data:
        user_id = validate_optional_id(data['user_id'], 'user_id inválido')
        _ensure_user_exists(user_id)
        task.user_id = user_id
    if 'category_id' in data:
        category_id = validate_optional_id(data['category_id'], 'category_id inválido')
        _ensure_category_exists(category_id)
        task.category_id = category_id
    if 'due_date' in data:
        task.due_date = parse_due_date(data['due_date'], 'Formato de data inválido')
    if 'tags' in data:
        task.tags = normalize_tags(data['tags'])

    task.updated_at = utc_now()
    task.save()
    logger.info('Task updated: %s', task.id)
    return task.to_dict()


def delete_task(task_id):
    _find_task(task_id).delete()
    logger.info('Task deleted: %s', task_id)
    return {'message': 'Task deletada com sucesso'}


def search_tasks(args, limit=None, offset=0):
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')
    tasks = Task.search(
        text=args.get('q', ''),
        status=args.get('status', ''),
        priority=parse_int_param(priority, 'Prioridade inválida') if priority else None,
        user_id=parse_int_param(user_id, 'user_id inválido') if user_id else None,
        limit=limit,
        offset=offset,
    )
    return [task.to_dict() for task in tasks]


def task_stats():
    by_status = Task.counts_by_status()
    total = Task.count()
    done = by_status.get('done', 0)
    return {
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': len(Task.overdue()),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
