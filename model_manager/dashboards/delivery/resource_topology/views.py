import copy
import json
import logging
import yaml

from collections import Counter
from model_manager.api.salt import salt_client
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import views

from .tables import ResourceTopologyTable
from .utils import get_topology_data

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ResourceTopologyTable
    template_name = "delivery/resource_topology/index.html"
    page_title = _("Resource Topology")

    def get_data(self):
        data = []
        try:
            res = salt_client.safe_low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'reclass.inventory'}])
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

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['polling_interval'] = getattr(settings, 'SALT_API_POLLING_INTERVAL', 30)
        return context


class HostDetailView(views.HorizonTemplateView):
    template_name = "delivery/resource_topology/host_detail.html"
    page_title = _("Host Detail - {{ host }}")

    def get_context_data(self, **kwargs):
        context = super(HostDetailView, self).get_context_data(**kwargs)

        try:
            res = salt_client.safe_low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'saltresource.host_data', 'arg': context.get('host', None)}])
            resource_data = res.get('return', [{'': ''}])[0].values()[0].get('graph')
        except Exception as e:
            resource_data = []
            LOG.error('Could not get host resource data from Salt Master API: %s' % repr(e))

        try:
            res = salt_client.safe_low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'reclass.node_pillar', 'arg': context.get('host', None)}])
            pillar_data = res.get('return', [{'': ''}])[0].values()[0].values()[0]
        except Exception as e:
            pillar_data = []
            LOG.error('Could not get host pillar data from Salt Master API: %s' % repr(e))

        try:
            pillar_data_f = yaml.safe_dump(pillar_data, default_flow_style=False)
        except:
            pillar_data_f = pillar_data

        context['resource_data'] = resource_data
        context['pillar_data'] = pillar_data_f

        return context


def topology_data_view(self, *args, **kwargs):
    domain = kwargs.get('domain', None)
    cache_ret = cache.get('topology_data', '{}')
    graph_data = json.loads(cache_ret)
    if not graph_data:
        graph_data = get_topology_data()

    filtered_data = copy.copy(graph_data)
    if domain:
       filtered_data = [d for d in graph_data if domain in d.get('host', '')]
       all_relations = [r.get('relations', [])[0] for r in filtered_data if r.get('relations', [])]
       external_hosts = [d for d in graph_data if d.get('host') in [r.get('host') for r in all_relations] and d.get('host') not in [f.get('host') for f in filtered_data]]
       filtered_data = filtered_data + external_hosts

    if filtered_data and isinstance(filtered_data, list):
        ret = {
            'result': 'ok',
            'data': filtered_data
        }
    else:
        ret = {
            'result': 'error',
            'data': repr(filtered_data)
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
        res = salt_client.safe_low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'reclass.node_pillar', 'arg': host}])
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

