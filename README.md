# Bookmarks project
Datastore and APIs for bookmarked reference material.

## Development

### Requirements

* git: https://git-scm.com/downloads
* Python 3: https://www.python.org/downloads/
* virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
* Postgres: https://www.postgresql.org/download/

### Getting Started

1. Install [git](https://git-scm.com/downloads), [Python 3](https://www.python.org/downloads/), and [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

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

1. Create `presterity` schema and user/role:

  ```sql
  psql
  postgres=# create schema presterity;
  postgres=# create user presterity password <password>;
  postgres=# grant all on schema presterity to presterity;
  ```

4. Connect to `presterity` database as `presterity` user and create schema:

  ```sql
  psql -U presterity -d presterity -h 127.0.0.1 -W
  presterity => \conninfo
  You are connected to database "presterity" as user "presterity" on host "127.0.0.1" at port "5432".
  SSL connection (cipher: DHE-RSA-AES256-GCM-SHA384, bits: 256)
  presterity => \i sql/bookmark-schema-001.sql
  CREATE FUNCTION
  psql:sql/bookmark-schema-001.sql:14: NOTICE:  table "bookmark" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE TRIGGER
  psql:sql/bookmark-schema-001.sql:58: NOTICE:  table "bookmark_topic" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE INDEX
  CREATE TRIGGER
  psql:sql/bookmark-schema-001.sql:78: NOTICE:  table "bookmark_note" does not exist, skipping
  DROP TABLE
  CREATE TABLE
  CREATE INDEX
  CREATE TRIGGER
  presterity => \dt
                List of relations
   Schema |      Name      | Type  |   Owner    
  --------+----------------+-------+------------
   public | bookmark       | table | presterity
   public | bookmark_note  | table | presterity
   public | bookmark_topic | table | presterity
  (3 rows)
  ```
