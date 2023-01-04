#!/bin/bash

set -e
set -o errexit
set -o pipefail
set -o nounset

# Another option is to use `pg_isready` command - But I didn't test it yet
postgres_ready() {
python << END
import sys
import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgresSQL to become available...'
  sleep 1
done
>&2 echo 'PostgresSQL is available'

python3 manage.py makemigrations --merge --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py initialize

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
