import logging

from collections import Counter
from devops_portal.api.salt import salt_client
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import views

from .tables import ResourceTopologyTable

RECLASS_DOMAIN = getattr(settings, 'RECLASS_DOMAIN', '')
LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ResourceTopologyTable
    template_name = "delivery/resource_topology/index.html"
    page_title = _("Resource Topology")

    def get_data(self):
        data = []
        res = salt_client.low([{'client': 'local', 'tgt': 'cfg01*', 'fun': 'reclass.inventory'}])
        # unwrap response from Salt Master
        inventory = res.get('return', [{'': ''}])[0].values()[0]
        domains = [".".join(n.split('.')[1:]) for n in inventory]
        counter = Counter(domains)
        for domain, count in counter.items():
            datum = {
                'domain': domain,
                'count': count
            }
            data.append(datum)

        return data


class DetailView(views.HorizonTemplateView):
    template_name = "delivery/resource_topology/detail.html"
    page_title = _("Resource Topology - {{ domain }}")


def topology_data_view(self, *args, **kwargs):
    data = []
    res = salt_client.low([{'client': 'local', 'tgt': 'cfg01*', 'fun': 'reclass.inventory'}])
    # unwrap response from Salt Master
    inventory = res.get('return', [{'': ''}])[0].values()[0]
    # create topology graph source data, optionally filtered by cluster name
    for node, node_data in inventory.items():
        if kwargs.get('domain', '') in node:
            roles = node_data.get('roles', [])
            if kwargs.get('domain', None):
                node = node.replace(kwargs.get('domain'), '')[:-1]
            for role in roles:
                datum = {
                    'name': ".".join([node, role]),
                    'lnkstrength': [],
                    'imports': []
                }
                data.append(datum)
                
    return JsonResponse(data, safe=False)

