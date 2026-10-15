#!/bin/bash
set -e  #stop à la 1ère erreur

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn monprojet.wsgi \
    --bind 0.0.0.0:8000 --workers 3