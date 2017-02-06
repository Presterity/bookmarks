# Bookmarks project
Datastore and APIs for bookmarked reference material.

## Development


### Requirements

* git: https://git-scm.com/downloads
* Python 3: https://www.python.org/downloads/
* virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
* Postgres: https://www.postgresql.org/download/


### Get the repo set up 

1. Install [git](https://git-scm.com/downloads), [Python 3](https://www.python.org/downloads/), and [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

1. Install Python Postgres adapter

  ```bash
  sudo apt-get install libpq-dev python3-dev
  ```

1. Get set up to [connect to github with ssh](https://help.github.com/articles/connecting-to-github-with-ssh/)

1. Create virtual environment and clone `bookmarks` repo:

  ```bash
  cd ~/projects
  virtualenv --python python3 --prompt presterity- venvs/presterity
  source venvs/presterity/bin/activate
  git clone git@github.com:presterity/bookmarks
  pip install -r requirements.txt
  ```


### Set up your database

1. Install [Postgres](https://www.postgresql.org/download/) ([Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04))

1. Create super user for yourself:

  ```bash
  sudo -i -u postgres
  createuser --interactive
  Enter name of role to add: <username>
  Shall the new role be a superuser? (y/n) y
  createdb <username>
  ```

1. Create local `presterity` schema and user/role:

  ```sql
  psql
  postgres=# create database presterity;
  postgres=# \c presterity;
  postgres=# create schema apps;
  postgres=# create user app_user with password 'resist';
  postgres=# alter role app_user set search_path to apps;
  postgres=# grant all on schema apps to app_user;
  ```

1. Connect to `presterity` database as `app_user` user and populate `apps` schema:

  ```sql
  psql -U app_user -d presterity -h localhost 
  presterity => \conninfo
  You are connected to database "presterity" as user "app_user" on host "127.0.0.1" at port "5432"
  SSL connection (cipher: DHE-RSA-AES256-GCM-SHA384, bits: 256)
  presterity => \i sql/001-bookmark-schema.sql;
  CREATE FUNCTION
  psql:sql/001-bookmark-schema.sql:14: NOTICE:  table "bookmark" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE TRIGGER
  psql:sql/001-bookmark-schema.sql:58: NOTICE:  table "bookmark_topic" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE INDEX
  CREATE TRIGGER
  psql:sql/001-bookmark-schema.sql:78: NOTICE:  table "bookmark_note" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE INDEX
  CREATE TRIGGER
  presterity => \dt
                List of relations
   Schema |      Name      | Type  |   Owner    
  --------+----------------+-------+------------
   apps   | bookmark       | table | app_user
   apps   | bookmark_note  | table | app_user
   apps   | bookmark_topic | table | app_user
  (3 rows)
  ```

1. Alternatively, use `mschematool` to populate `apps` schema:

  ```bash
  export MSCHEMATOOL_CONFIG=/ws/git/presterity/bookmarks/migration.py 
  mschematool local init_db
  mschematool local to_sync
  mschematool local sync
  ```




