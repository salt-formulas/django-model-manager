import json

from celery import Task
from django.conf import settings
from django.core.cache import cache

from .resource_topology.utils import get_topology_data


class CacheTopologyData(Task):
    name = "cache_topology_data"
    ignore_result = True

    def run(*args, **kwargs):
        ret = get_topology_data()
        cache.set('topology_data', json.dumps(ret), 5 * 60)

