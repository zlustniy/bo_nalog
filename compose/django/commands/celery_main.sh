#!/usr/bin/env bash

set -e

celery -A project worker \
  --loglevel=error \
  --queues=celery \
  --concurrency=${CONCURRENCY:-1} \
  --hostname=main \
  --events \
  --without-gossip \
  --without-mingle \
  --without-heartbeat \
