import horizon
from django.utils.translation import ugettext_lazy as _


class SaltControl(horizon.Panel):
    name = _("Salt Minion Control")
    slug = 'salt_control'
