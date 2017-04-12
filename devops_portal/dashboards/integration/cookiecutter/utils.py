import json
import requests
import socket

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

'''
We can get cookiecutter.json using one of the private get_context methods, for example: _get_context_github

{
    "cluster_name"                              : "deployment_name",
    "cluster_domain"                            : "deploy-name.local",
    "public_host"                               : "${_param:openstack_proxy_address}",
    "reclass_repository"                        : "https://github.com/Mirantis/mk-lab-salt-model.git",

    "deploy_network_netmask"                    : "255.255.255.0",
    "deploy_network_gateway"                    : "",
    "control_network_netmask"                   : "255.255.255.0",
    ...
}

generate_context method uses get_context method of choice and transforms remote JSON into form fields schema:

    INFRA_JSON_URL = 'https://api.github.com/repos/Mirantis/mk2x-cookiecutter-reclass-model/contents/cluster_product/infra/cookiecutter.json'

    ctx = generate_context('github', 'infra', 'Infra', **{'url': INFRA_JSON_URL})
    print ctx

Results in:
    [{
        'fieldset_name': 'infra',
        'fieldset_label': _('Infra'),
        'fields': {
            'deploy_network_netmask': {'field_template': 'IP', 'kwargs': {'initial': '255.255.255.0'}},
            'deploy_network_gateway': {'field_template': 'IP'},
            'control_network_netmask': {'field_template': 'IP', 'kwargs': {'initial': '255.255.255.0'}},
            'dns_server01': {'field_template': 'IP', 'kwargs': {'initial': '8.8.8.8'}},
            'dns_server02': {'field_template': 'IP', 'kwargs': {'initial': '8.8.4.4'}},
            'control_vlan': {'field_template': 'TEXT', 'kwargs': {'initial': '10'}},
            'tenant_vlan': {'field_template': 'TEXT', 'kwargs': {'initial': '20'}},
            ...
        }
    }]
    
'''

INFRA_JSON_URL = 'https://api.github.com/repos/Mirantis/mk2x-cookiecutter-reclass-model/contents/cluster_product/infra/cookiecutter.json'


def _get_context_github(url):
    s = requests.Session()
    token = getattr(settings, 'GITHUB_TOKEN', None)
    s.headers.update({'Accept': 'application/vnd.github.v3.raw'})
    if token:
        s.headers.update({'Authorization': 'token ' + str(token)})
    r = s.get(url)
    ctx = json.loads(r.text)

    return ctx


def _is_ipaddress(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def generate_context(source, name, label, **kwargs):
    ctx = {}
    if 'github' in source:
        url = kwargs.get('url')
        ctx = [{
            'fieldset_name': name,
            'fieldset_label': label,
            'fields': {}
        }]
        remote_ctx = _get_context_github(url)
        if isinstance(remote_ctx, dict):
            fields = ctx[0]['fields']
            for field, value in remote_ctx.items():
                params = {}
                params['field_template'] = 'TEXT'
                if value:
                    if _is_ipaddress(value):
                        params['field_template'] = 'IP'
                    else:
                        params['field_template'] = 'TEXT'
                    params['kwargs'] = {'initial': value}
                fields[field] = params

    return ctx

