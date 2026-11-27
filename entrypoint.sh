#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_default_superuser
exec gunicorn partitionmusic.wsgi:application \
    --bind 0.0.0.0:8000 --workers 3