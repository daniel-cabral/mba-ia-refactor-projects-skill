from config.constants import DEFAULT_CATEGORY_COLOR
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from utils.validators import (
    require_json_object,
    validate_category_description,
    validate_category_name,
    validate_color,
)

CATEGORY_NOT_FOUND = 'Categoria não encontrada'


def _find_category(category_id):
    category = Category.find(category_id)
    if not category:
        raise NotFoundError(CATEGORY_NOT_FOUND)
    return category


def list_categories(limit=None, offset=0):
    task_counts = Task.counts_by_category()
    result = []
    for category in Category.list_all(limit, offset):
        data = category.to_dict()
        data['task_count'] = task_counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(data):
    require_json_object(data)
    if not data.get('name'):
        raise ValidationError('Nome é obrigatório')

    category = Category(
        name=validate_category_name(data['name']),
        description=validate_category_description(data.get('description', '')),
        color=validate_color(data.get('color', DEFAULT_CATEGORY_COLOR)),
    )
    category.save()
    return category.to_dict()


def update_category(category_id, data):
    category = _find_category(category_id)
    require_json_object(data)

    if 'name' in data:
        category.name = validate_category_name(data['name'])
    if 'description' in data:
        category.description = validate_category_description(data['description'])
    if 'color' in data:
        category.color = validate_color(data['color'])

    category.save()
    return category.to_dict()


def delete_category(category_id):
    _find_category(category_id).delete()
    return {'message': 'Categoria deletada'}
