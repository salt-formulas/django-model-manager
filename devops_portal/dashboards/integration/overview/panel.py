import horizon
from django.utils.translation import ugettext_lazy as _
from devops_portal.dashboards.integration import dashboard


class Overview(horizon.Panel):
    name = _("Overview")
    slug = 'overview'


dashboard.Integration.register(Overview)
