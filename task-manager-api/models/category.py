from sqlalchemy import select

from config.constants import DEFAULT_CATEGORY_COLOR
from database import db
from models.base import CrudMixin, apply_page
from utils.helpers import utc_now


class Category(CrudMixin, db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_CATEGORY_COLOR)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    @classmethod
    def list_all(cls, limit=None, offset=0):
        statement = apply_page(select(cls).order_by(cls.id), limit, offset)
        return db.session.execute(statement).scalars().all()

    @classmethod
    def count(cls):
        return db.session.scalar(select(db.func.count(cls.id)))
