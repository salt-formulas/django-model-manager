from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Delivery(horizon.Dashboard):

    name = _('Delivery Dashboard')
    slug = 'delivery'

horizon.register(Delivery)

