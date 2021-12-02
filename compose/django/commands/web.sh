#!/usr/bin/env bash

python manage.py migrate --noinput
gunicorn project.wsgi -w ${GUNICORN_WORKERS:-1} -b 0.0.0.0:5000 --chdir=/webapp
