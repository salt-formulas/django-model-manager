import horizon
from django.utils.translation import ugettext_lazy as _


class ResourceTopology(horizon.Panel):
    name = _("Resource Topology")
    slug = 'resource_topology'
