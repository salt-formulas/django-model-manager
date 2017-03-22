from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Model(horizon.PanelGroup):

    name = _('Model')
    slug = 'model'
    panels = ('cookiecutter', )
#    permissions = ("devops_portal.operator",)


class DevopsPortal(horizon.Dashboard):

    name = _(getattr(settings, 'DEVOPS_PORTAL_DASHBOARD_NAME', _("DevOps Portal")))
    slug = "devops_portal"
    panels = (Tickets, Identity,)
    default_panel = "cookiecutter"


horizon.register(DevopsPortal)
