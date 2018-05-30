from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ResourceTopologyDetailLink(tables.LinkAction):
    name = "resource_topology_detail"
    verbose_name = _("Detail")
    url = "horizon:delivery:resource_topology:detail"


class ResourceTopologyTable(tables.DataTable):
    domain = tables.Column('domain', verbose_name=_("Domain"))
    count = tables.Column('count', verbose_name=_('Node Count'))

    def get_object_id(self, datum):
        return datum.get('domain')

    class Meta(object):
        name = 'resource_topology'
        row_actions = [ResourceTopologyDetailLink]
