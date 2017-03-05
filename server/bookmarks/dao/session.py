"""Database session management."""

import logging
from subprocess import check_call

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from .settings import PRESTERITY_DB_URL, PRESTERITY_ENV

__all__ = ('Session',
           'init_local_db')

log = logging.getLogger(__name__)


class Session(object):
    """Utility class for managing SQLAlchemy session."""

    # Scoped session registry; to be 
    _session = None
    
    @classmethod
    def _initialize(cls):
        """Create scoped session.

        This should be called once per process.
        """
        if cls._session:
            log.info("Session has already been initialized")
        else:
            log.info("Connecting to db %s", PRESTERITY_DB_URL)
            engine = sa.create_engine(PRESTERITY_DB_URL, client_encoding='utf8')
            cls._session = sa_orm.scoped_session(sa_orm.sessionmaker(bind=engine))

    @classmethod
    def get(cls):
        """Return scoped session, creating it if necessary."""
        if cls._session is None:
            cls._initialize()
        return cls._session

    @classmethod
    def close(cls, commit=True):
        """Close session and return it to connection pool, optionally committing before doing so.
        """
        if cls._session is not None:
            if commit:
                cls._session.commit()
            cls._session.remove()

