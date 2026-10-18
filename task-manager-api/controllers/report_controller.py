from datetime import timedelta

from config.constants import HIGH_PRIORITY_THRESHOLD, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utc_now


def _completion_rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


def summary_report():
    now = utc_now()
    by_status = Task.counts_by_status()
    by_priority = Task.counts_by_priority()
    completion_by_user = Task.completion_by_user()
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    overdue_tasks = Task.overdue()
    overdue_list = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (now - task.due_date).days,
        }
        for task in overdue_tasks
    ]

    user_stats = []
    for user in User.list_all():
        total, completed = completion_by_user.get(user.id, (0, 0))
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': _completion_rate(completed, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count(),
            'total_users': User.count(),
            'total_categories': Category.count(),
        },
        'tasks_by_status': {
            'pending': by_status.get('pending', 0),
            'in_progress': by_status.get('in_progress', 0),
            'done': by_status.get('done', 0),
            'cancelled': by_status.get('cancelled', 0),
        },
        'tasks_by_priority': {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(since),
            'tasks_completed_last_7_days': Task.count_completed_since(since),
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = User.find(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.for_user(user_id)
    total = len(tasks)
    count_by_status = {}
    for task in tasks:
        count_by_status[task.status] = count_by_status.get(task.status, 0) + 1
    done = count_by_status.get('done', 0)

    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': count_by_status.get('pending', 0),
            'in_progress': count_by_status.get('in_progress', 0),
            'cancelled': count_by_status.get('cancelled', 0),
            'overdue': sum(1 for task in tasks if task.is_overdue()),
            'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
            'completion_rate': _completion_rate(done, total),
        },
    }
