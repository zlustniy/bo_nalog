#!/usr/bin/env bash

set -e

celery -A project worker \
  --loglevel=error \
  --queues=load_pages \
  --concurrency=${CONCURRENCY:-1} \
  --hostname=load_pages \
  --events \
  --without-gossip \
  --without-mingle \
  --without-heartbeat \
