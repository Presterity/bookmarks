"""Settings for the presterity DAO layer."""

import os


# PRESTERITY_ENV: str.
# A string representing the environment to use for PRESTERITY. Should be one of
# 'local', 'dev', or 'prod'.
PRESTERITY_ENV = os.environ.get('PRESTERITY_ENV', 'local')
_PRESTERITY_ENVS = ['local', 'dev', 'prod']
assert PRESTERITY_ENV in _PRESTERITY_ENVS, "PRESTERITY_ENV must be one of '{}'.".format(
    ', '.join(_PRESTERITY_ENVS))


# PRESTERITY_DB_URL: str
# URL string for the database
_POSTGRES_CONNECTION_STRING = 'postgresql://{user}:{password}@{netloc_and_port}/{database}'
if PRESTERITY_ENV == 'local':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='presterity_apps',
        password='resist',
        netloc_and_port='localhost',
        database='presterity')
elif PRESTERITY_ENV == 'dev':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='presterity_apps',
        password=os.environ['PRESTERITY_DEV_PASSWORD'],
        netloc_and_port='presterity-dev.civm9kvdku8h.us-west-2.rds.amazonaws.com:5432',
        database='presterity')
elif PRESTERITY_ENV == 'prod':
    PRESTERITY_DB_URL = _POSTGRES_CONNECTION_STRING.format(
        user='presterity_apps',
        password=os.environ['PRESTERITY_PROD_PASSWORD'],
        netloc_and_port='presterity-prod.civm9kvdku8h.us-west-2.rds.amazonaws.com:5432',
        database='presterity')
