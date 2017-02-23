"""Low-level functionality for creating and connecting to database."""

import logging
from subprocess import check_call

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from .settings import PRESTERITY_DB_URL, PRESTERITY_ENV

__all__ = ('get_session',
           'init_local_db')

log = logging.getLogger(__name__)
_engine = None


def get_connection():
    return _ensure_engine().connect()

def get_session():
    engine = _ensure_engine()
    Session = sa_orm.sessionmaker(bind=engine)
    return Session(bind=engine.connect())

def init_local_db():
    """Create presterity/apps using mschematool.

    Only ever do this in local environment
    """
    if PRESTERITY_ENV != 'local':
        raise ValueError("Refusing to create local database in environment '{0}'".format(
                PRESTERITY_ENV))

    print("initializing database", flush=True)
    check_call("echo \"create database presterity\" | psql", shell=True)
    check_call("echo \"create schema apps\" | psql presterity", shell=True)
    check_call("echo \"create user app_user with password 'resist'\" | psql presterity", shell=True)
    check_call("echo \"alter role app_user set search_path to apps\" | psql presterity", shell=True)
    check_call("echo \"grant all on schema apps to app_user\" | psql presterity", shell=True)
    check_call("mschematool --config migration.py local init_db", shell=True)
    check_call("mschematool --config migration.py local sync", shell=True)
    print("database initialized", flush=True)
    init_local_db.already_init = True


# private

def _ensure_engine():
    """Return sqlalchemy db engine, initializing if necessary."""
    global _engine
    if not _engine:
        log.info("Connecting to db %s", PRESTERITY_DB_URL)
        _engine = sa.create_engine(PRESTERITY_DB_URL, client_encoding='utf8')
    return _engine
    
