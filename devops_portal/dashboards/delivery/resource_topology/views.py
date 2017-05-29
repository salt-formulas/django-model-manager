import logging

from devops_portal.api.salt import salt_client
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from horizon.views import HorizonTemplateView

LOG = logging.getLogger(__name__)


class IndexView(HorizonTemplateView):
    template_name = "delivery/resource_topology/index.html"
    page_title = _("Resource Topology")

    def get_data(self):
        return {}


def topology_data_view(self, *args, **kwargs):
    res = salt_client.low([{'client': 'local', 'tgt': 'cfg01*', 'fun': 'reclass.inventory'}])
    # unwrap response from Salt Master
    inventory = res.get('return', [{'': ''}])[0].values()[0]
    data = []
    reclass_cluster = getattr(settings, 'RECLASS_CLUSTER', '')
    # create topology graph source data, optionally filtered by cluster name
    for node, node_data in inventory.items():
        if reclass_cluster in node:
            roles = node_data.get('roles', [])
            for role in roles:
                datum = {
                    'name': ".".join([node, role]),
                    'lnkstrength': [],
                    'imports': []
                }
                data.append(datum)
                
    return JsonResponse(data, safe=False)

