
import logging
from .base import BaseClient
LOG = logging.getLogger(__name__)


class Operator(BaseClient):

    scope = 'users'

    search_options = {
        'operator': True
    }


class User(BaseClient):

    scope = 'users'

    operators = Operator()

    search_options = {
        'operator': False
    }

    def update_own_password(self, id, data, request=None):
        return self.request(
            '/users/{}/set_password/'.format(id),
            "POST", data, request=request)

    def login(self, data, request):
        return self.request(
            '/auth/login/',
            'POST',
            params=data,
            request=request)

    def logout(self, data, request=None):
        return self.request(
            '/auth/logout/',
            'POST',
            params=data,
            request=request)
