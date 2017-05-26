from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Integration(horizon.Dashboard):

    name = getattr(settings, 'DEVOPS_PORTAL_NAME', _('Integration Dashboard'))
    slug = 'integration'
    default_panel = 'modeldesigner'

    def nav(self, context):
        dash = context['request'].horizon.get('dashboard', None)
        if dash and dash.slug == self.slug:
            return True
        return False


horizon.register(Integration)

