from sqlalchemy import case, func, select
from sqlalchemy.orm import joinedload

from config.constants import (
    DEFAULT_PRIORITY,
    DEFAULT_TASK_STATUS,
    FINISHED_STATUSES,
    STATUS_DONE,
)
from database import db
from models.base import CrudMixin, apply_page
from utils.helpers import utc_now


class Task(CrudMixin, db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_TASK_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_summary_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': str(self.due_date) if self.due_date else None,
        }

    def is_overdue(self):
        if not self.due_date:
            return False
        return self.due_date < utc_now() and self.status not in FINISHED_STATUSES

    # --- queries -------------------------------------------------------

    @classmethod
    def list_with_relations(cls, limit=None, offset=0):
        statement = apply_page(
            select(cls).options(joinedload(cls.user), joinedload(cls.category)).order_by(cls.id),
            limit,
            offset,
        )
        return db.session.execute(statement).unique().scalars().all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None, limit=None, offset=0):
        statement = select(cls)
        if text:
            statement = statement.where(
                db.or_(cls.title.contains(text, autoescape=True), cls.description.contains(text, autoescape=True))
            )
        if status:
            statement = statement.where(cls.status == status)
        if priority is not None:
            statement = statement.where(cls.priority == priority)
        if user_id is not None:
            statement = statement.where(cls.user_id == user_id)
        statement = apply_page(statement.order_by(cls.id), limit, offset)
        return db.session.execute(statement).scalars().all()

    @classmethod
    def for_user(cls, user_id):
        return db.session.execute(select(cls).where(cls.user_id == user_id).order_by(cls.id)).scalars().all()

    @classmethod
    def count(cls):
        return db.session.scalar(select(func.count(cls.id)))

    @classmethod
    def counts_by_status(cls):
        rows = db.session.execute(select(cls.status, func.count(cls.id)).group_by(cls.status)).all()
        return {status: total for status, total in rows}

    @classmethod
    def counts_by_priority(cls):
        rows = db.session.execute(select(cls.priority, func.count(cls.id)).group_by(cls.priority)).all()
        return {priority: total for priority, total in rows}

    @classmethod
    def counts_by_user(cls):
        rows = db.session.execute(select(cls.user_id, func.count(cls.id)).group_by(cls.user_id)).all()
        return {user_id: total for user_id, total in rows}

    @classmethod
    def counts_by_category(cls):
        rows = db.session.execute(select(cls.category_id, func.count(cls.id)).group_by(cls.category_id)).all()
        return {category_id: total for category_id, total in rows}

    @classmethod
    def completion_by_user(cls):
        """Return {user_id: (total, done)} in a single grouped query."""
        done = func.sum(case((cls.status == STATUS_DONE, 1), else_=0))
        rows = db.session.execute(select(cls.user_id, func.count(cls.id), done).group_by(cls.user_id)).all()
        return {user_id: (total, int(done_count or 0)) for user_id, total, done_count in rows}

    @classmethod
    def overdue(cls):
        statement = (
            select(cls)
            .where(cls.due_date.is_not(None), cls.due_date < utc_now(), cls.status.not_in(FINISHED_STATUSES))
            .order_by(cls.id)
        )
        return db.session.execute(statement).scalars().all()

    @classmethod
    def count_created_since(cls, moment):
        return db.session.scalar(select(func.count(cls.id)).where(cls.created_at >= moment))

    @classmethod
    def count_completed_since(cls, moment):
        return db.session.scalar(
            select(func.count(cls.id)).where(cls.status == STATUS_DONE, cls.updated_at >= moment)
        )
