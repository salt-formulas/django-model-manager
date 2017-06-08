import json
import logging

from celery import Task
from celery.decorators import periodic_task
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache

from .resource_topology.utils import get_topology_data

LOG = logging.getLogger(__name__)
POLLING_INTERVAL = getattr(settings, 'SALT_API_POLLING_INTERVAL', 30)


@periodic_task(run_every=timedelta(seconds=POLLING_INTERVAL))
def cache_topology_data():
    lock_interval = interval = POLLING_INTERVAL
    if lock_interval < 30:
        lock_interval = 30
    acquire_lock = lambda: cache.add('cache_topology_data_lock', 'true', 5 * lock_interval)
    release_lock = lambda: cache.delete('cache_topology_data_lock')

    if acquire_lock():
        LOG.info('Obtaining topology data from Salt Master ...')
        try:
            ret = get_topology_data()
            cache.set('topology_data', json.dumps(ret), 5 * interval)
        except Exception as e:
            LOG.error('Failed to obtain topology data from Salt master: %s' % repr(e))
            release_lock()
        finally:
            release_lock()
    else:
        LOG.info('Another instance of cache_topology_data is already running, skipping ...')

    return True

