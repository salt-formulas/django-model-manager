import csv
import yaml

from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .utils import GeneratedAction


class GeneralParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    class Meta(object):
        name = _("General parameters")
        slug = "general_params_action"


class InfraParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    class Meta(object):
        name = _("Infrastructure parameters")
        slug = "infra_params_action"


class ProductParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    class Meta(object):
        name = _("Product parameters")
        slug = "product_params_action"


def should_use_block(value):
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def my_represent_scalar(self, tag, value, style=None):
    if style is None:
        if should_use_block(value):
            style = '|'
            value = value.replace('\r', '')
        else:
            style = self.default_style

    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node


class MaaSMachinesDatum:
    '''Example input kwargs:

      {
        'subnet': 'deploy_network',
        'ip': '${_param:infra_kvm_node01_deploy_address}',
        'power_type': 'ipmi',
        'power_user': 'foo',
        'node_name': 'kvm01',
        'mac': '00:11:22:33:44:55',
        'power_address': '176.16.10.100',
        'mode': 'static',
        'power_password': 'strongpassword',
        'gateway': '${_param:deploy_network_gateway}'
      }
    '''

    def __init__(
        self,
        node_name=None,
        subnet=None,
        ip=None,
        mac=None,
        mode=None,
        gateway=None,
        power_type=None,
        power_user=None,
        power_address=None,
            power_password=None):

        self._node_name = node_name
        self._subnet = subnet
        self._ip = ip
        self._mac = mac
        self._mode = mode
        self._gateway = gateway
        self._power_type = power_type
        self._power_user = power_user
        self._power_address = power_address
        self._power_password = power_password

    def get_dict(self):
        _dict = {}
        if all([self._subnet, self._ip, self._mode, self._gateway]):
            _dict = {
                self._node_name: {
                    'interface': {
                        'subnet': self._subnet,
                        'ip': self._ip,
                        'mac': self._mac,
                        'mode': self._mode,
                        'gateway': self._gateway
                    },
                    'power_parameters': {
                        'power_type': self._power_type,
                        'power_user': self._power_user,
                        'power_address': self._power_address,
                        'power_password': self._power_password
                    }
                }
            }
        else:
            _dict = {
                self._node_name: {
                    'interface': {
                        'mac': self._mac,
                    },
                    'power_parameters': {
                        'power_type': self._power_type,
                        'power_user': self._power_user,
                        'power_address': self._power_address,
                        'power_password': self._power_password
                    }
                }
            }
        return _dict

    def get_yaml(self):
        return yaml.safe_dump(self.get_dict(), default_flow_style=False)

    def __str__(self):
        return self.get_yaml()

    def __repr__(self):
        return '<%s: %s>' % (
            self.__class__.__name__, self._node_name)

    def __dict__(self):
        return self.get_dict()


class MaaSMachinesData:
    '''Helper template for data from MAC address file field.

    filedata: list of MaaSMachinesDatum dictionaries
    '''

    def __init__(self, filedata):
        self.filedata = []
        for datum in filedata:
            self.filedata.append(MaaSMachinesDatum(**datum))
        self._count = len(self.filedata)

    def get_dict(self):
        _dict = {}
        for datum in self.filedata:
            _dict.update(datum.get_dict())
        return _dict

    def get_yaml(self):
        return yaml.safe_dump(self.get_dict(), default_flow_style=False)

    def __str__(self):
        return self.get_yaml()

    def __repr__(self):
        return '<%s: %d items>' % (
            self.__class__.__name__, self._count)

    def __dict__(self):
        return self.get_dict()


def process_file(field_name, file_obj, seed):
    file_csv = csv.DictReader(file_obj)
    file_instance = MaaSMachinesData([r for r in file_csv])
    file_data = file_instance.get_yaml()
    file_fields = cache.get('meta_file_fields_{}'.format(seed), {})
    file_fields.update({field_name: file_data})
    cache.set('meta_file_fields_{}'.format(seed), file_fields, 3600)
    return file_data


class CookiecutterContextAction(workflows.Action):
    """
    TODO: document this action
    """
    cookiecutter_context = forms.CharField(widget=forms.Textarea(attrs={'rows': '40'}))

    def __init__(self, request, context, *args, **kwargs):
        super(CookiecutterContextAction, self).__init__(
            request, context, *args, **kwargs)
        seed = context.get('context_seed', '-')
        cookiecutter_ctx = {
            'default_context': {
                k: v
                for (k, v)
                in context.items()
                if v is not None and k != 'cookiecutter_context'
            }
        }
        transform_bools = {
            k: str(v)
            for (k, v)
            in cookiecutter_ctx['default_context'].items()
            if isinstance(v, bool)
        }
        cookiecutter_ctx['default_context'].update(transform_bools)
        process_files = {k: process_file(k, v, seed)
                         for (k, v)
                         in cookiecutter_ctx['default_context'].items()
                         if isinstance(v, InMemoryUploadedFile)}

        file_fields = cache.get('meta_file_fields_{}'.format(seed), {})
        for field_name, field_data in file_fields.items():
            cookiecutter_ctx['default_context'][field_name] = field_data

        cookiecutter_ctx['default_context'].update(process_files)
        yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar
        self.fields['cookiecutter_context'].initial = yaml.safe_dump(cookiecutter_ctx,
                                                                     default_flow_style=False)
        # TODO: this basically makes the field uneditable,
        # but it is necessary to deliver correct initial value
        self.initial['cookiecutter_context'] = self.fields['cookiecutter_context'].initial

    class Meta(object):
        name = _("Output summary")
