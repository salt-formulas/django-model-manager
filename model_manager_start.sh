#!/bin/bash
NAME="devops_portal"
DJANGODIR=/srv/devops-portal
USER=www-data
GROUP=www-data
NUM_WORKERS=4
DJANGO_SETTINGS_MODULE="devops_portal.settings.base"
DJANGO_WSGI_MODULE=devops_portal.wsgi

# Activate the virtual environment
cd $DJANGODIR
source /srv/devops-portal/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /srv/devops-portal/venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --log-file=/var/log/devops_portal/gunicorn.log \
  --bind=0.0.0.0:8081 \
  --timeout=600

