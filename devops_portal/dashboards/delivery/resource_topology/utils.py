import logging

from devops_portal.api.salt import salt_client

LOG = logging.getLogger(__name__)


def get_topology_data():
    '''
    Get topology data from configured Salt Master
    '''
    data = []
    try:
        res = salt_client.low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'reclass.graph_data'}]) 
    except:
        res = {}
        LOG.error('Could not get topology data from Salt Master API.')

    try:
        status_res = salt_client.low([{'client': 'local', 'tgt': 'salt:master', 'expr_form': 'pillar', 'fun': 'saltresource.graph_data'}]) 
    except:
        status_res = {}
        LOG.error('Could not get status data from Salt Master API.')

    try:
        graph_data = res.get('return', [{'': ''}])[0].values()[0].get('graph')
    except:
        graph_data = []

    try:
        status_data = status_res.get('return', [{'': ''}])[0].values()[0].get('graph')
    except:
        status_data = []

    for datum in graph_data:
        status_datum = [r for r in status_data if r.get('host') == datum.get('host') and r.get('service') == datum.get('service')]
        if status_datum:
            status = status_datum[0].get('status', 'unknown')
            datum['status'] = status

        for relation in datum.get('relations', []):
            relation['status'] = datum.get('status', 'unknown')

    return graph_data

