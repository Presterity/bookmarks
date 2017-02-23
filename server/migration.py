"""A configuration file for the bookmarks tables.

This file provides configuration for mschematool, which we can use to 
create and migrate the database.

https://github.com/aartur/mschematool
"""

import os

DATABASES = {
    'local': {
        'migrations_dir': './sql/',
        'engine': 'postgres',
        'dsn': 'postgresql://app_user:resist@localhost/presterity'
    },
    'dev': {
        'migrations_dir': './sql/',
        'engine': 'postgres',
        'dsn': 'postgresql://app_user:{password}@somehost:someport/presterity'.format(
            password=os.getenv('PRESTERITY_DEV_DB_PASSWORD', ''))
    },
    'prod': {
        'migrations_dir': './sql/',
        'engine': 'postgres',
        'dsn': 'postgresql://app_user:{password}@somehost:someport/presterity'.format(
            password=os.getenv('PRESTERITY_PROD_DB_PASSWORD', ''))
    }
}


LOG_FILE = './migration.log'
