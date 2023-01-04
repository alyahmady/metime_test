# MeTime test project

This project include an authentication/authorization system

Make sure that you have **Docker and Docker Compose** installed, before you build the project with Docker.
[Download](https://docs.docker.com/compose/install/)

## Production build (Docker)

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Local build (Docker)

```bash
docker-compose -f docker-compose.local.yml up -d --build
```

## Local build (without Docker)

1- Please check you have **Python 3**, **PostgreSQL** and **Redis** installed.
 * [Python](https://www.python.org/downloads/)
 * [PostgreSQL](https://www.postgresql.org/download/)
 * [Redis](https://redis.io/docs/getting-started/installation/)


2- Then you need a virtual environment for the project, and have it activated.

**Windows**
```bash
cd <PROJECT_DIR>
python -m venv .venv
.venv\Scripts\activate
```

**Linux**
```bash
cd <PROJECT_DIR>
python3 -m venv .venv
.venv/bin/activate
```

3- After that you should install project dependencies.

```bash
pip install requirements.txt
```

4- Then you need to check and set configurations of the project.

* First, make a copy of the example configurations:

    **Windows**
    ```bash
    copy .\deploy\environments\.env.example .\deploy\environments\.env
    ```
  
    **Linux**
    ```bash
    cp ./deploy/environments/.env.example ./deploy/environments/.env
    ```

* Take a look at the file in this address, with a text editor and change as you wish

    **Windows**
    ```bash
    notepad.exe .\deploy\environments\.env
    ```
  
    **Linux**
    ```bash
    nano ./deploy/environments/.env
    ```
  
  * **It's better the re-set all password fields for more security.** If you did so, please take a look at other `env` files within `environments` directory, to set passwords of other related services, as well. **Please consider that username, password, and port configs of Redis and Postgres must be synced within all of these three files:**
    * `.env`
    * `.env.nginx`
    * `.env.postgres`
  * You need to create your database and user on your local PostgreSQL server, before you set configurations with `POSTGRES_` prefix. To do so, you can run these queries on your PostgreSQL.
  
      ```bash
      CREATE DATABASE <POSTGRES_DB>;
      CREATE USER <POSTGRES_USER> WITH PASSWORD '<POSTGRES_PASSWORD>';
      ALTER ROLE <POSTGRES_USER> SET client_encoding TO 'utf8';
      ALTER ROLE <POSTGRES_USER> SET default_transaction_isolation TO 'read committed';
      ALTER ROLE <POSTGRES_USER> SET timezone TO 'UTC';
      GRANT ALL PRIVILEGES ON DATABASE <POSTGRES_DB> TO <POSTGRES_USER>;
      ```

5- To call APIs or test project, you need to have `celery` process, running on your system

**Windows**
```bash
celery -A metime worker -l INFO --pool=solo
```

**Linux**
```bash
celery -A metime worker -l INFO
```

6- Before finishing the build process, if you want to make sure of test cases, you can run this command.

```bash
python manage.py test
```

* Please consider that, You may have failures experience in tests, for Celery async tasks, on Windows. To make sure of test cases, it's better to run `test` command on a linux instance.

7- To initialize Database and static files, run these commands:

```bash
python manage.py makemigrations --merge --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py initialize
```

  * For not experiencing pages without static files, you need to set `DEBUG` config as `True` within `metime/settings.py`.

8- Run this commands, to start the project development server:

**Linux**
```bash
python manage.py runserver 0.0.0.0:8000
```

* If you want to run project on a more secure and stable server, instead of `runserver` command, follow as below:

```bash
gunicorn --workers=10 --bind=0.0.0.0:8000 metime.asgi:application -k uvicorn.workers.UvicornWorker --timeout 1000
```

**You project now is running on your _localhost_ on _8000_ port.**

  * Admin Page -> [localhost:8000/admin](localhost:8000/admin)
  * Swagger -> [localhost:8000/api/swagger](localhost:8000/api/swagger)

APIs

  * Login (POST) -> [localhost:8000/auth/token](localhost:8000/auth/token)
  * Refresh Token (POST) -> [localhost:8000/auth/token/refresh](localhost:8000/auth/token/refresh)
  * User Register (POST) -> [localhost:8000/users](localhost:8000/users)
  * User Profile (PATCH) -> [localhost:8000/users/USER_ID](localhost:8000/users/1)
  * Password Change (PUT) -> [localhost:8000/users/USER_ID/password](localhost:8000/users/1/password)