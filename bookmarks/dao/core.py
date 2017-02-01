"""Creation of database."""

import logging

import sqlalchemy

from .settings import PRESTERITY_DB_URL


log = logging.getLogger(__name__)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        log.info("creating engine on %s", PRESTERITY_DB_URL)
        _engine = sqlalchemy.create_engine(PRESTERITY_DB_URL)
    return _engine


