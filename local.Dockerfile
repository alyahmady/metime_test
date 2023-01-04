FROM python:3.10-slim AS compile-image
LABEL maintainer="better.aly.ahmady@gmail.com"

RUN apt-get update; \
    apt-get install -yqq --no-install-recommends --show-progress \
    build-essential gcc software-properties-common python3-psycopg2

COPY requirements.txt .
RUN pip install --quiet --user wheel
RUN pip install --quiet --user -r requirements.txt


FROM python:3.10-slim AS build-image

COPY --from=compile-image /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Set environment variables.
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN apt-get update && \
    apt-get install -yqq --no-install-recommends --show-progress \
    supervisor wget nano curl

RUN mkdir -p /code/logs

# It's a bad practice to hardcode directories
# But for security and image performance, it will be a good practice :)
COPY auth_app /code/auth_app
COPY metime /code/metime
COPY users_app /code/users_app
COPY manage.py /code/manage.py

# Supervisor config
RUN mkdir -p /var/log/supervisor

ADD ./.supervisord/supervisord.conf /etc/supervisor/supervisord.conf
ADD ./.supervisord/api.conf /etc/supervisor/conf.d/api.conf
ADD ./.supervisord/celery_worker.conf /etc/supervisor/conf.d/celery_worker.conf
ADD ./.supervisord/celery_flower.conf /etc/supervisor/conf.d/celery_flower.conf

WORKDIR /code

EXPOSE 8000

COPY deploy/entrypoints/entrypoint.sh /code/deploy/entrypoints/entrypoint.sh
RUN sed -i 's/\r$//g' /code/deploy/entrypoints/entrypoint.sh
RUN chmod +x /code/deploy/entrypoints/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/code/deploy/entrypoints/entrypoint.sh"]
HEALTHCHECK --start-period=5s --interval=2s --timeout=5s --retries=8 CMD curl --fail http://localhost:8000/health || exit 1
