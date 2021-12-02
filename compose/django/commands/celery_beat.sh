#!/usr/bin/env bash

set -e

celery -A project beat \
  --pidfile= \
  --loglevel=info \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler \
