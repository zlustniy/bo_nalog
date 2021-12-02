#!/bin/bash
set -e
cmd="$@"
/wait
echo "Starting ... $cmd"

case "$1" in
  gunicorn) /commands/web.sh ;;
  celery-beat) /commands/celery_beat.sh ;;
  celery-main) /commands/celery_main.sh ;;
  celery-load-pages) /commands/celery_load_pages.sh ;;
  celery-load-files) /commands/celery_load_files.sh ;;
  asgi) /commands/web_asgi.sh ;;
  cron) /commands/cron.sh ;;
  test ) /commands/test.sh ;;
  *) exec $@ ;;
esac