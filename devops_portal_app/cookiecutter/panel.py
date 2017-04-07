import horizon
from devops_portal import dashboard
from django.utils.translation import ugettext_lazy as _


class Cookiecutter(horizon.Panel):
    name = _("Cookiecutter")
    slug = 'cookiecutter'
#    permissions = ("devops_portal.operator",)


dashboard.DevopsPortal.register(Cookiecutter)
