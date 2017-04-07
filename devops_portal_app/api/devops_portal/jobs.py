
import logging
from .base import BaseClient

LOG = logging.getLogger(__name__)


class Job(BaseClient):

    scope = 'organisations'

    def summary(self, id, request=None):
        return self.request(
            '/%s/%s/summary' % (self.scope, id),
            'GET',
            request=request)
