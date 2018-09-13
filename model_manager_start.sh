#!/bin/bash
NAME="model_manager"
DJANGODIR=/srv/model-manager
USER=www-data
GROUP=www-data
NUM_WORKERS=4
DJANGO_SETTINGS_MODULE="model_manager.settings.base"
DJANGO_WSGI_MODULE=model_manager.wsgi

# Activate the virtual environment
cd $DJANGODIR
source /srv/model-manager/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /srv/model-manager/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --log-file=/var/log/model-manager/gunicorn.log \
  --bind=0.0.0.0:8081 \
  --timeout=600

