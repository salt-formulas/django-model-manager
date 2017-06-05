import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pepper import Pepper

LOG = logging.getLogger(__name__)


def get_client():
    # get salt client config
    url = getattr(settings, 'SALT_API_URL', '127.0.0.1')
    user = getattr(settings, 'SALT_API_USER', None)
    password = getattr(settings, 'SALT_API_PASSWORD', None)
    eauth = getattr(settings, 'SALT_API_EATH', 'pam')
    if not user or not password:
        msg = 'SALT_API_USER and SALT_API_PASSWORD settings must not be empty.'
        raise ImproperlyConfigured(msg)

    # instantiate client
    try:
        c = Pepper(url)
        # call login to get token on client instance
        login = c.login(user, password, eauth)
    except:
        c = None
        LOG.error('Could not connect to Salt Master API.')

    return c

salt_client = get_client()

