from sqlalchemy import func, select
from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import DEFAULT_ROLE
from database import db
from models.base import CrudMixin, apply_page, commit_or_rollback
from utils.helpers import utc_now


class User(CrudMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == 'admin'

    def delete_with_tasks(self):
        """Delete the user and their tasks in one transaction."""
        for task in list(self.tasks):
            db.session.delete(task)
        db.session.delete(self)
        commit_or_rollback()

    @classmethod
    def list_all(cls, limit=None, offset=0):
        statement = apply_page(select(cls).order_by(cls.id), limit, offset)
        return db.session.execute(statement).scalars().all()

    @classmethod
    def find_by_email(cls, email):
        return db.session.execute(select(cls).where(cls.email == email)).scalars().first()

    @classmethod
    def count(cls):
        return db.session.scalar(select(func.count(cls.id)))
