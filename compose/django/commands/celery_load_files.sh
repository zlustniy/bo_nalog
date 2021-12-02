#!/usr/bin/env bash

set -e

celery -A project worker \
  --loglevel=error \
  --queues=load_files \
  --concurrency=${CONCURRENCY:-1} \
  --hostname=load_files \
  --events \
  --without-gossip \
  --without-mingle \
  --without-heartbeat \
