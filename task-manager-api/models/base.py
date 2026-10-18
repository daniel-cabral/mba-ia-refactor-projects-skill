import logging

from sqlalchemy.exc import SQLAlchemyError

from database import db

logger = logging.getLogger(__name__)


def commit_or_rollback():
    """Commit the current unit of work; roll back and re-raise on failure."""
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception('Database commit failed')
        raise


def apply_page(statement, limit=None, offset=0):
    if limit is not None:
        statement = statement.limit(limit)
    if offset:
        statement = statement.offset(offset)
    return statement


class CrudMixin:
    @classmethod
    def find(cls, record_id):
        return db.session.get(cls, record_id)

    def save(self):
        db.session.add(self)
        commit_or_rollback()

    def delete(self):
        db.session.delete(self)
        commit_or_rollback()
