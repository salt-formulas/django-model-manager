from django.conf import settings
from model_manager.api.utils.decorators import timeout
from pepper import Pepper


@timeout(10)
def _login(client):
    user = getattr(settings, 'SALT_API_USER', 'salt')
    password = getattr(settings, 'SALT_API_PASSWORD', 'salt')
    eauth = getattr(settings, 'SALT_API_EAUTH', 'pam')
    client.login(user, password, eauth)
    return True


url = getattr(settings, 'SALT_API_URL')
c = Pepper(url)
_login(c)

