import logging

from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from model_manager.api.utils.decorators import timeout
from pepper import Pepper
from time import time

LOG = logging.getLogger(__name__)
SALT_API_URL = getattr(settings, 'SALT_API_URL', '127.0.0.1')
try:
    SALT_CLIENT = Pepper(SALT_API_URL)
except:
    LOG.error('Could not connect to Salt Master API.')
    SALT_CLIENT = None


class SaltClientExtension():

    @timeout(10)
    def _login(self):
        client = self.client
        if client.auth:
            ts = client.auth.get('expire', str(time()))
            expires = datetime.fromtimestamp(ts)
            now = datetime.now()
            if now > expires:
                return client

        username = getattr(settings, 'SALT_API_USER', 'salt')
        password = getattr(settings, 'SALT_API_PASSWORD', 'salt')
        eauth = getattr(settings, 'SALT_API_EAUTH', 'pam')

        try:
            auth = client.req('/login', {
                'username': username,
                'password': password,
                'eauth': eauth}).get('return', [{}])[0]
        except Exception as e:
            LOG.error('Could not authenticate against Salt Master API: %s' % repr(e))
            auth = {}

        return auth

    def safe_low(self, *args, **kwargs):
        client = self.client
        try:
            client.auth = client._login()
        except:
            pass

        return client.low(*args, **kwargs)


if SALT_CLIENT:
    extension = SaltClientExtension()
    extension.client = SALT_CLIENT

    for method in [method for method in dir(extension)
                   if callable(getattr(extension, method)) and not method.startswith("__")]:

        setattr(SALT_CLIENT, method, getattr(extension, method))

    try:
        SALT_CLIENT.auth = SALT_CLIENT._login()
    except:
        pass

    salt_client = SALT_CLIENT
else:
    salt_client = None
