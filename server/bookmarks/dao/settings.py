"""Settings for the presterity DAO layer."""

import logging
import os

log = logging.getLogger(__name__)


# PRESTERITY_ENV: str.
# A string representing the environment to use for PRESTERITY. Should be one of
# 'local', 'dev', or 'prod'.
PRESTERITY_ENV = os.environ.get('PRESTERITY_ENV', 'local')
_PRESTERITY_ENVS = ['local', 'dev', 'prod']
if PRESTERITY_ENV not in _PRESTERITY_ENVS:
    log.warn("Unexpected value '{0}' for PRESTERITY_ENV; expected one of {1}".format(
            PRESTERITY_ENV, ', '.join(_PRESTERITY_ENVS)))


# URL string for the database
PRESTERITY_DB_URL = None
_POSTGRES_CONNECTION_STRING = 'postgresql://{user}:{password}@{netloc_and_port}/{database}'
if PRESTERITY_ENV == 'local':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='app_user',
        password='resist',
        netloc_and_port='localhost',
        database='presterity')
elif PRESTERITY_ENV == 'dev':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='app_user',
        password=os.environ['PRESTERITY_DEV_PASSWORD'],
        netloc_and_port='somehost:someport',
        database='presterity')
elif PRESTERITY_ENV == 'prod':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='app_user',
        password=os.environ['PRESTERITY_PROD_PASSWORD'],
        netloc_and_port='somehost:someport',
        database='presterity')
