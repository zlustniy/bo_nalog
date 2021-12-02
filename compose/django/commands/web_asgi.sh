#!/usr/bin/env bash

python manage.py migrate --noinput
gunicorn project.asgi -w ${GUNICORN_ASYNC_WORKERS:-1} -b 0.0.0.0:5001 --chdir=/webapp -k uvicorn.workers.UvicornWorker
