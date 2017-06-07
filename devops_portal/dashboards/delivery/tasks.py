import json
import logging

from celery import Task
from django.conf import settings
from django.core.cache import cache

from .resource_topology.utils import get_topology_data

LOG = logging.getLogger(__name__)


class CacheTopologyData(Task):
    name = 'cache_topology_data'
    ignore_result = True

    def run(*args, **kwargs):
        lock_interval = interval = getattr(settings, 'SALT_API_POLLING_INTERVAL', 30)
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

