from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Integration(horizon.Dashboard):

    name = getattr(settings, 'DEVOPS_PORTAL_NAME', _('Integration'))
    slug = 'integration'
    default_panel = 'modeldesigner'

horizon.register(Integration)

