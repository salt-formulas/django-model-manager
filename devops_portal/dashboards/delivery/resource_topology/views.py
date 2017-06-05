import logging
import yaml

from collections import Counter
from devops_portal.api.salt import salt_client
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import views

from .tables import ResourceTopologyTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ResourceTopologyTable
    template_name = "delivery/resource_topology/index.html"
    page_title = _("Resource Topology")

    def get_data(self):
        data = []
        try:
            res = salt_client.low([{'client': 'local', 'tgt': 'cfg01*', 'fun': 'reclass.inventory'}])
        except:
            res = {}
            LOG.error('Could not get response from Salt Master API.')
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
    try:
        res = salt_client.low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'reclass.graph_data'}]) 
    except:
        res = {}
        LOG.error('Could not get response from Salt Master API.')

    try:
        graph_data = res.get('return', [{'': ''}])[0].values()[0].get('graph')
    except:
        graph_data = res.get('return', [{'': ''}])[0].values()[0]

    if graph_data and isinstance(graph_data, list):
        ret = {
            'result': 'ok',
            'data': graph_data
        }
    else:
        ret = {
            'result': 'error',
            'data': repr(graph_data)
        }
    return JsonResponse(ret)


def status_data_view(self, *args, **kwargs):
    data = []
    try:
        res = salt_client.low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'saltresource.graph_data'}]) 
    except:
        res = {}
        LOG.error('Could not get response from Salt Master API.')

    try:
        graph_data = res.get('return', [{'': ''}])[0].values()[0].get('graph')
    except:
        graph_data = res.get('return', [{'': ''}])[0].values()[0]

    if graph_data and isinstance(graph_data, list):
        ret = {
            'result': 'ok',
            'data': graph_data
        }
    else:
        ret = {
            'result': 'error',
            'data': repr(graph_data)
        }
    return JsonResponse(ret)


def pillar_data_view(self, *args, **kwargs):
    data = []
    # recreate minion ID from domain and chart node name
    domain = kwargs.get('domain')
    host = kwargs.get('host')
    service = kwargs.get('service')
    system = service.split('.')[0]
    subsystem = service.split('.')[1]

    try:
        res = salt_client.low([{'client': 'local', 'tgt': 'cfg01*', 'fun': 'reclass.node_pillar', 'arg': host}])
    except:
        res = {}
        LOG.error('Could not get response from Salt Master API.')

    # unwrap response from Salt Master
    pillar = res.get('return', [{'': ''}])[0].values()[0]
    pillar_data = pillar.values()[0].get(system, {}).get(subsystem, {})
    pillar_yaml = yaml.safe_dump(pillar_data, default_flow_style=False)
    html = '<pre>' + pillar_yaml + '</pre>'
    ret = {
        'result': 'ok',
        'html': html
    }

    return JsonResponse(ret)

