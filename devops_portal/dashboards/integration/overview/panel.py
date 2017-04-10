import horizon
from django.utils.translation import ugettext_lazy as _


class Overview(horizon.Panel):
    name = _("Overview")
    slug = 'overview'
