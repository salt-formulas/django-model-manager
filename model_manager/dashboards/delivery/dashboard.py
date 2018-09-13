from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Delivery(horizon.Dashboard):

    name = _('Delivery')
    slug = 'delivery'

horizon.register(Delivery)
