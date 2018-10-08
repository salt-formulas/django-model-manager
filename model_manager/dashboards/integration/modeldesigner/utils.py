import ceph_cfg
import copy
import crypt
import io
import json
import logging
import re
import requests
import socket
import uuid
import yaml

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from django import forms
from django import http
from django import shortcuts
from django import template
from django.conf import settings
from django.core import exceptions as django_exc
from django.core.cache import cache
from django.utils.encoding import force_text, force_bytes
from django.utils.translation import ugettext_lazy as _
from docutils.core import publish_parts
from horizon import exceptions as horizon_exc
from horizon import messages
from horizon import workflows
from horizon.workflows.base import WorkflowContext
from ipaddress import IPv4Network
from jinja2 import Environment, meta
from pygerrit.rest import GerritRestAPI
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from os import urandom

from .forms import Fieldset, FileField, CharField, BooleanField, IPField, ChoiceField

LOG = logging.getLogger(__name__)


####################################
# GET CONTEXT FROM REMOTE LOCATION #
####################################

class ContextTemplateCollector(object):
    '''
    TODO: document this class
    '''
    url = None
    path = None
    remote = None
    username = None
    password = None
    token = None

    def __init__(self, *args, **kwargs):
        default_url = getattr(settings, 'COOKIECUTTER_CONTEXT_URL', None)
        default_path = getattr(settings, 'COOKIECUTTER_CONTEXT_PATH', None)
        default_remote = getattr(settings, 'COOKIECUTTER_CONTEXT_REMOTE', None)
        default_username = getattr(settings, 'COOKIECUTTER_CONTEXT_USERNAME', None)
        default_password = getattr(settings, 'COOKIECUTTER_CONTEXT_PASSWORD', None)
        default_token = getattr(settings, 'COOKIECUTTER_CONTEXT_TOKEN', None)
        default_versions = getattr(settings, 'COOKIECUTTER_CONTEXT_VERSIONS', [])
        default_project_name = getattr(settings, 'COOKIECUTTER_CONTEXT_PROJECT_NAME', None)
        default_file_name = getattr(settings, 'COOKIECUTTER_CONTEXT_FILE_NAME', None)
        default_version_filter = getattr(settings, 'COOKIECUTTER_CONTEXT_VERSION_FILTER', None)
        default_version_map = getattr(settings, 'COOKIECUTTER_CONTEXT_VERSION_MAP', {})

        self.url = kwargs.get('url', default_url)
        self.path = kwargs.get('path', default_path)
        self.remote = kwargs.get('remote', default_remote)
        self.username = kwargs.get('username', default_username)
        self.password = kwargs.get('password', default_password)
        self.token = kwargs.get('token', default_token)
        self.versions = kwargs.get('versions', default_versions)
        self.project_name = kwargs.get('project_name', default_project_name)
        self.file_name = kwargs.get('file_name', default_file_name)
        self.version_filter = kwargs.get('version_filter', default_version_filter)
        self.version_map = kwargs.get('version_map', default_version_map)

        self.collectors = {
            'github': {
                'collector': self._github_collector,
                'version_collector': self._static_version_collector
            },
            'http': {
                'collector': self._http_collector,
                'version_collector': self._static_version_collector
            },
            'gerrit': {
                'collector': self._gerrit_collector,
                'version_collector': self._gerrit_version_collector
            },
            'localfs': {
                'collector': self._localfs_collector,
                'version_collector': self._static_version_collector
            }
        }

    def _gerrit_get(self, endpoint_url):
        auth = HTTPBasicAuth(self.username, self.password)
        rest = GerritRestAPI(url=self.url, auth=auth)
        response_body = ''
        try:
            response_body = rest.get(endpoint_url)
        except HTTPError as e:
            msg = "Failed to get response from Gerrit URL %s: %s" % (endpoint_url, str(e))
            LOG.error(msg)
        except Exception as e:
            LOG.exception(e)
        return response_body

    def _gerrit_collector(self, version=None):
        if not self.username:
            msg = """ Gerrit username is required to be set as COOKIECUTTER_CONTEXT_USERNAME
                      with COOKIECUTTER_CONTEXT_REMOTE = "gerrit". """
            raise django_exc.ImproperlyConfigured(msg)
        if not self.password:
            msg = """ Gerrit password is required to be set as COOKIECUTTER_CONTEXT_PASSWORD
                      with COOKIECUTTER_CONTEXT_REMOTE = "gerrit". """
            raise django_exc.ImproperlyConfigured(msg)
        if not self.url:
            msg = """ Gerrit base URL is required to be set as COOKIECUTTER_CONTEXT_URL
                      with COOKIECUTTER_CONTEXT_REMOTE = "gerrit". """
            raise django_exc.ImproperlyConfigured(msg)
        if not self.project_name:
            msg = """ Gerrit project name is required to be set as COOKIECUTTER_CONTEXT_PROJECT_NAME
                      with COOKIECUTTER_CONTEXT_REMOTE = "gerrit". """
            raise django_exc.ImproperlyConfigured(msg)
        if not self.file_name:
            msg = """ Gerrit context file name is required to be set as COOKIECUTTER_CONTEXT_FILE_NAME
                      with COOKIECUTTER_CONTEXT_REMOTE = "gerrit". """
            raise django_exc.ImproperlyConfigured(msg)

        cache_key = 'workflow_context'
        endpoint_url = '/projects/%s/branches/master/files/%s/content' % (self.project_name, self.file_name)
        if version:
            versions = self._gerrit_get_versions()
            if version in self.version_map.values():
                version = [v[0] for v in self.version_map.items() if v[1] == version][0]
            revision = versions.get(version)
            cache_key = 'workflow_context_%s' % revision
            endpoint_url = '/projects/%s/commits/%s/files/%s/content' % (
                self.project_name, revision, self.file_name)

        cached_ctx = cache.get(cache_key, None)
        if cached_ctx:
            return cached_ctx

        ctx = self._gerrit_get(endpoint_url)
        cache.set(cache_key, ctx, 3600)
        return ctx

    def _gerrit_get_versions(self):
        cache_key = 'workflow_versions_%s_%s' % (self.url, self.project_name)
        cached_versions = cache.get(cache_key, None)
        if cached_versions:
            return cached_versions

        tags_endpoint_url = '/projects/%s/tags/' % self.project_name
        master_endpoint_url = '/projects/%s/branches/master/' % self.project_name

        tags = self._gerrit_get(tags_endpoint_url)
        master = self._gerrit_get(master_endpoint_url)

        self.versions = {}
        for tag in tags:
            key = tag['ref'].replace('refs/tags/', '')
            self.versions[key] = tag['revision']
        self.versions['master'] = master['revision']

        # manually add specific review commit for development purposes
        # self.versions['mm_devel'] = '7a5ad84f09e16d48c190319f82cc556eab9aeb40'

        cache.set(cache_key, self.versions, 3600)
        return self.versions

    def _gerrit_version_collector(self):
        versions = self._gerrit_get_versions()
        return list(versions.keys())

    def _github_collector(self, version=None):
        session = requests.Session()

        cached_ctx = cache.get('workflow_context', None)
        if cached_ctx:
            return cached_ctx

        if not self.url:
            msg = """ Github repository API URL is required to be set as COOKIECUTTER_CONTEXT_URL
                      with COOKIECUTTER_CONTEXT_REMOTE = "github". """
            raise django_exc.ImproperlyConfigured(msg)

        if not self.token:
            msg = """ Github API token is required to be set as COOKIECUTTER_CONTEXT_TOKEN
                      with COOKIECUTTER_CONTEXT_REMOTE = "github". """
            raise django_exc.ImproperlyConfigured(msg)

        session.headers.update({'Accept': 'application/vnd.github.v3.raw'})
        session.headers.update({'Authorization': 'token ' + str(self.token)})
        response = session.get(self.url)
        if response.status_code >= 300:
            try:
                response_json = json.loads(str(response.text))
                response_text = response_json['message']
            except:
                response_text = response.text
            msg = "Could not get remote file from Github:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (
                str(response.status_code), response_text)
            LOG.error(msg)
            ctx = ""
        else:
            ctx = response.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    def _http_collector(self, version=None):
        session = requests.Session()

        cached_ctx = cache.get('workflow_context', None)
        if cached_ctx:
            return cached_ctx

        if not self.url:
            msg = """ HTTP URL is required to be set as COOKIECUTTER_CONTEXT_URL
                      with COOKIECUTTER_CONTEXT_REMOTE = "http". """
            raise django_exc.ImproperlyConfigured(msg)

        if self.username and self.password:
            response = session.get(self.url, auth=(self.username, self.password))
        else:
            response = session.get(self.url)

        if response.status_code >= 300:
            msg = "Could not get remote file from HTTP URL %s:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (
                self.url, str(response.status_code), response.text)
            LOG.error(msg)
            ctx = ""
        else:
            ctx = response.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    def _localfs_collector(self, version=None):
        if not self.path:
            msg = """ Path to file on local filesystem is required to be set as
                      COOKIECUTTER_CONTEXT_PATH with COOKIECUTTER_CONTEXT_REMOTE = "localfs". """
            raise django_exc.ImproperlyConfigured(msg)

        try:
            with io.open(self.path, 'r') as file_handle:
                ctx = file_handle.read()
        except Exception as e:
            msg = "Could not read file %s: %s" % (self.path, repr(e))
            LOG.error(msg)
            ctx = ""

        return ctx

    def _static_version_collector(self):
        return self.versions

    def collect_template(self, version=None):
        if version:
            versions = self.collect_versions()
            if version not in versions:
                LOG.warning('Selected version %s not available, using default. Available versions: %s' % (
                    version, versions))
                version = None

        collector = self.collectors.get(self.remote, {}).get('collector', lambda: '')
        return collector(version)

    def collect_versions(self):
        collector = self.collectors.get(self.remote, {}).get('version_collector', lambda: [])
        versions = collector()

        # filter versions by configured regular expression
        if self.version_filter:
            regex = re.compile(self.version_filter)
            versions = filter(regex.search, versions)

        # replace version names by names configured in version map
        for idx, version in enumerate(versions):
            if version in self.version_map:
                versions[idx] = self.version_map[version]

        return sorted(versions)


######################################################
# WORKFLOW ACTION AND STEP WITH AUTOGENERATED FIELDS #
######################################################

# Custom Jinja2 filters

def subnet(subnet, host_ip):
    """
    Create network object and get host by index

    Example:

        Context
        -------
        {'my_subnet': '192.168.1.0/24'}

        Template
        --------
        {{ my_subnet|subnet(1) }}

        Output
        ------
        192.168.1.1
    """
    if not subnet:
        return ""

    if '/' not in subnet:
        subnet = str(subnet) + '/24'

    try:
        network = IPv4Network(unicode(subnet))
        idx = int(host_ip) - 1
        ipaddr = str(list(network.hosts())[idx])
    except IndexError:
        ipaddr = _("Host index is out of range of available addresses")
    except:
        ipaddr = subnet.split('/')[0]

    return ipaddr


def netmask(subnet):
    """
    Create network object and get netmask

    Example:

        Context
        -------
        {'my_subnet': '192.168.1.0/24'}

        Template
        --------
        {{ my_subnet|netmask }}

        Output
        ------
        255.255.255.0
    """
    if not subnet:
        return ""

    if '/' not in subnet:
        subnet = str(subnet) + '/24'

    try:
        network = IPv4Network(unicode(subnet))
        netmask = str(network.netmask)
    except:
        netmask = "Cannot determine network mask"

    return netmask


def generate_password(length):
    """
    Generate password of defined length

    Example:

        Template
        --------
        {{ 32|generate_password }}

        Output
        ------
        Jda0HK9rM4UETFzZllDPbu8i2szzKbMM
    """
    chars = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ1234567890"

    return "".join(chars[ord(c) % len(chars)] for c in urandom(length))


def hash_password(password):
    """
    Hash password

    Example:

        Context
        -------
        {'some_password': 'Jda0HK9rM4UETFzZllDPbu8i2szzKbMM'}

        Template
        --------
        {{ some_password|hash_password }}

        Output
        ------
        $2b$12$HXXew12E9mN3NIXv/egSDurU.dshYQRepBoeY.6bfbOOS5IyFVIBa
    """
    chars = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ"
    salt_str = "".join(chars[ord(c) % len(chars)] for c in urandom(8))
    salt = "$6$%s$" % salt_str
    pw_hash = ''
    if password:
        pw_hash = crypt.crypt(password, salt)

    return pw_hash


CUSTOM_FILTERS = [
    ('subnet', subnet),
    ('generate_password', generate_password),
    ('hash_password', hash_password),
    ('netmask', netmask)
]


def generate_ssh_keypair(seed=None):
    if not seed:
        private_key_str = ""
        public_key_str = ""
    else:
        private_key_cache = 'private_key_' + str(seed)
        public_key_cache = 'public_key_' + str(seed)
        cached_private_key = cache.get(private_key_cache)
        cached_public_key = cache.get(public_key_cache)

        if cached_private_key and cached_public_key:
            private_key_str = cached_private_key
            public_key_str = cached_public_key

        else:
            private_key_obj = rsa.generate_private_key(
                backend=default_backend(),
                public_exponent=65537,
                key_size=2048
            )

            public_key_obj = private_key_obj.public_key()

            public_key = public_key_obj.public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)

            private_key = private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption())

            private_key_str = private_key.decode('utf-8')
            public_key_str = public_key.decode('utf-8')

            cache.set(private_key_cache, private_key_str, 3600)
            cache.set(public_key_cache, public_key_str, 3600)

    return (private_key_str, public_key_str)


def generate_uuid():
    return uuid.uuid4()


def generate_ceph_keyring(cluster_uuid, keyring_type, seed):
    if not cluster_uuid:
        return ''

    keyring_cache = 'keyring_%s_%s_%s' % (keyring_type, cluster_uuid, seed)
    cached_keyring = cache.get(keyring_cache)

    if cached_keyring:
        return cached_keyring

    keyring_kwargs = {
        'cluster_name': 'ceph',
        'cluster_uuid': cluster_uuid,
        'keyring_type': keyring_type
    }

    out = ceph_cfg.keyring_create(**keyring_kwargs)
    key_start = out.find('key') + 6
    key_end = out.find('==') + 2
    keyring = out[key_start:key_end]

    cache.set(keyring_cache, keyring, 3600)

    return keyring


CUSTOM_FUNCTIONS = [
    ('generate_ssh_keypair', generate_ssh_keypair),
    ('generate_uuid', generate_uuid),
    ('generate_ceph_keyring', generate_ceph_keyring)
]

# Extended workflow classes

DOCUTILS_RENDERER_SETTINGS = {
    'initial_header_level': 2,
    # important, to have even lone titles stay in the html fragment:
    'doctitle_xform': False,
    # we also disable the promotion of lone subsection title to a subtitle:
    'sectsubtitle_xform': False,
    'file_insertion_enabled': False,  # SECURITY MEASURE (file hacking)
    'raw_enabled': False,             # SECURITY MEASURE (script tag)
    'report_level': 2,                # report warnings and above, by default
}


class GeneratedAction(workflows.Action):
    """ TODO: Document this class
    """
    global_context = {}
    field_templates = {
        "TEXT": {
            "class": CharField,
            "args": tuple(),
            "kwargs": {
                "max_length": 255,
                "label": "",
                "initial": "",
                "required": True,
                "help_text": ""
            }
        },
        "LONG_TEXT": {
            "class": CharField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "initial": "",
                "required": True,
                "widget": forms.Textarea(attrs={'rows': '20'}),
                "help_text": ""
            }
        },
        "IP": {
            "class": IPField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "initial": "",
                "required": True,
                "mask": False
            }
        },
        "BOOL": {
            "class": BooleanField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "initial": False,
                "required": False
            }
        },
        "CHOICE": {
            "class": ChoiceField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "choices": [],
                "required": False
            }
        },
        "FILE": {
            "class": FileField,
            "args": tuple(),
            "kwargs": {
                "max_length": 255,
                "label": "",
                "required": False,
                "help_text": ""
            }
        }
    }

    def __init__(self, request, context, *args, **kwargs):
        if request.method == "POST":
            forms.Form.__init__(self, request.POST, request.FILES, initial=context)
        else:
            forms.Form.__init__(self, initial=context)

        if not hasattr(self, "handle"):
            raise AttributeError("The action %s must define a handle method."
                                 % self.__class__.__name__)
        self.request = request
        self._populate_choices(request, context)
        self.required_css_class = 'required'

        rendered_context = self.render_context(context)
        for fieldset in rendered_context:
            if not self.requirements_met(fieldset, context):
                continue

            self.help_text += self.render_doc(fieldset.get('doc', ''))
            fieldset_name = fieldset.get('name')
            fieldset_label = fieldset.get('label')
            fields = fieldset.get('fields')
            # create fieldset
            self.fields["fieldset_" + fieldset_name] = Fieldset(
                name=fieldset_name,
                label=fieldset_label
            )
            # iterate over fields dictionary
            for field in fields:
                if not self.requirements_met(field, context):
                    continue

                # get field schema from FIELDS and set params
                field_templates = copy.deepcopy(self.field_templates)
                field_template = field_templates[field['type']]
                field_cls = field_template['class']
                field_args = field_template['args']
                field_kw = field_template['kwargs']
                # set kwargs
                field_kw['fieldset'] = fieldset_name
                field_kw['label'] = field.get('label', self.deslugify(field['name']))
                field_kw['help_text'] = field.get('help_text', None)
                field_kw['initial'] = field.get('initial', None)
                field_kw['width'] = field.get('width', 'full')
                if 'required' in field:
                    field_kw['required'] = field['required']
                # template specific params
                if 'CHOICE' in field['type']:
                    field_kw['choices'] = field['choices']
                    field_kw['extend_context'] = field.get('extend_context', False)
                if 'IP' in field['type'] and 'mask' in field:
                    field_kw['mask'] = field['mask']
                # declare field on self
                self.fields[field['name']] = field_cls(*field_args, **field_kw)
                if field.get('readonly', False):
                    try:
                        self.fields[field['name']].widget.attrs['readonly'] = True
                    except:
                        pass
                if field.get('hidden', False):
                    self.fields[field['name']].widget = forms.HiddenInput()
                # workaround for empty strings in inital data after ``contribute`` is defined
                # TODO: find out why this is happening
                if (field['name'] in self.initial and
                        (self.initial[field['name']] == '' or self.initial[field['name']] is None)):
                    self.initial[field['name']] = field.get('initial', None)

    @staticmethod
    def deslugify(string):
        return str(string).replace('_', ' ').capitalize()

    def get_context_template(self):
        version = self.request.GET.get('version', None)
        if not version:
            version = self.request.META.get('HTTP_X_HORIZON_CONTEXT_VERSION', None)
        self.global_context['_cookiecutter_version'] = \
            version or getattr(settings, 'COOKIECUTTER_CONTEXT_DEFAULT_VERSION', '')
        ctx_tmpl_collector = ContextTemplateCollector()
        ctx_tmpl = ctx_tmpl_collector.collect_template(version)

        return ctx_tmpl

    def render_context(self, context):
        env = Environment()
        for fltr in CUSTOM_FILTERS:
            env.filters[fltr[0]] = fltr[1]
        for fnc in CUSTOM_FUNCTIONS:
            env.globals[fnc[0]] = fnc[1]
        source_context = self.get_context_template()
        tmpl = env.from_string(source_context)
        parsed_source = env.parse(source_context)

        # update context with global context
        context.update(self.global_context)

        tmpl_ctx_keys = meta.find_undeclared_variables(parsed_source)
        for key in tmpl_ctx_keys:
            if key not in env.globals:
                if (key not in context) or (key in context and context[key] is None):
                    context[key] = ""
        try:
            ctx = yaml.load(tmpl.render(context))
        except:
            ctx = yaml.load(source_context)
        if not isinstance(ctx, dict):
            return {}
        return ctx[self.slug]

    def render_doc(self, value, header_level=None, report_level=None):
        settings_overrides = DOCUTILS_RENDERER_SETTINGS.copy()
        if header_level is not None:  # starts from 1
            settings_overrides["initial_header_level"] = header_level
        if report_level is not None:  # starts from 1 too
            settings_overrides["report_level"] = report_level
        parts = publish_parts(source=force_bytes(value),
                              writer_name="html4css1",
                              settings_overrides=settings_overrides)
        trimmed_parts = parts['html_body'][23:-8]
        return force_text(trimmed_parts)

    def requirements_met(self, item, context):
        """Return True if all requirements for this field/fieldset are met
        """
        if context and 'requires' in item:
            for req in item['requires']:
                key = req.keys()[0]
                value = req.values()[0]
                if (key not in context) or (key in context and not value == context[key]):
                    return False
        if context and 'requires_or' in item:
            score = 0
            for req in item['requires_or']:
                key = req.keys()[0]
                value = req.values()[0]
                if key in context and value == context[key]:
                    score += 1
            if score == 0:
                return False

        return True


class GeneratedStep(workflows.Step):
    """ TODO: Document this class
    """
    template_name = "integration/modeldesigner/workflow/_workflow_step_with_fieldsets.html"
    depends_on = tuple()
    contributes = tuple()
    global_context = {}

    def __init__(self, *args, **kwargs):
        super(GeneratedStep, self).__init__(*args, **kwargs)
        ctx = self.render_context()
        # get lists of fields
        field_lists = [x['fields'] for x in ctx]
        # flatten the lists
        field_list = [item for sublist in field_lists for item in sublist]
        contributes = list(self.contributes)
        for field in field_list:
            if field['name'] not in contributes:
                contributes.append(field['name'])
        self.contributes = tuple(contributes)

    def contribute(self, data, context):
        super(GeneratedStep, self).contribute(data, context)

        excluded_fields = ['csrfmiddlewaretoken', 'cookiecutter_context']
        for key, value in data.items():
            if value and key not in excluded_fields and key not in context:
                context.update({key: value})
                if key not in self.contributes:
                    self.contributes += (key,)
                if key not in self.workflow.contributions:
                    self.workflow.contributions.add(key)

        # update shared context with option Bool values according to choices made in ChoiceList fields
        choice_fields = [
            obj
            for obj
            in self.action.fields.values()
            if hasattr(obj, 'choices') and getattr(obj, 'extend_context',  False)
        ]
        choices = [chc[0] for fld in choice_fields for chc in fld.choices]
        for choice in choices:
            context[choice] = True if choice in context.values() else False
        return context

    def get_context_template(self):
        version = self.workflow.request.GET.get('version')
        self.global_context['_cookiecutter_version'] = \
            version or getattr(settings, 'COOKIECUTTER_CONTEXT_DEFAULT_VERSION', '')
        ctx_tmpl_collector = ContextTemplateCollector()
        ctx_tmpl = ctx_tmpl_collector.collect_template(version)

        return ctx_tmpl

    def render_context(self):
        context = {}
        env = Environment()
        for fltr in CUSTOM_FILTERS:
            env.filters[fltr[0]] = fltr[1]
        for fnc in CUSTOM_FUNCTIONS:
            env.globals[fnc[0]] = fnc[1]
        source_context = self.get_context_template()

        tmpl = env.from_string(source_context)
        parsed_source = env.parse(source_context)

        # update context with global context
        context.update(self.global_context)

        tmpl_ctx_keys = meta.find_undeclared_variables(parsed_source)
        for key in tmpl_ctx_keys:
            if key not in env.globals:
                context[key] = ""
        try:
            ctx = yaml.load(tmpl.render(context))
        except:
            ctx = yaml.load(source_context)
        if not isinstance(ctx, dict):
            return {}
        return ctx[self.action_class.slug]


class GeneratedWorkflow(workflows.Workflow):
    async_wizard = True
    multipart = True
    exclusions = ['csrfmiddlewaretoken']

    def __init__(self, request=None, context_seed=None, entry_point=None,
                 *args, **kwargs):
        super(GeneratedWorkflow, self).__init__(request, context_seed, entry_point, *args, **kwargs)

        self.exclusions = set([])

        for step in self.steps:
            if hasattr(step, 'excludes'):
                self.exclusions = self.exclusions | set(step.excludes)

        # Override filtered context from parent class.
        self.context = WorkflowContext(self)
        context_seed = context_seed or {}
        clean_seed = dict([(key, val)
                           for key, val in context_seed.items()
                           if key not in self.exclusions])
        self.context_seed = clean_seed
        self.context.update(clean_seed)

        if request and request.method == "POST":
            for step in self.steps:
                valid = step.action.is_valid()
                # Be sure to use the CLEANED data if the workflow is valid.
                if valid:
                    data = step.action.cleaned_data
                else:
                    data = request.POST
                self.context = step.contribute(data, self.context)

        # contribute choice field options to workflow context as Bools
        for step in self.steps:
            choice_fields = [
                obj
                for obj
                in step.action.fields.values()
                if hasattr(obj, 'choices') and getattr(obj, 'extend_context', False)
            ]
            choices = [chc[0] for fld in choice_fields for chc in fld.choices]
            for choice in choices:
                if choice not in self.context.keys():
                    self.context[choice] = True if choice in self.context.values() else False

    def get_absolute_url(self):
        return self.request.get_full_path()

    def _verify_contributions(self, context):
        return True


class AsyncWorkflowView(workflows.WorkflowView):
    """
    Overrides default WF functionality
    """
    def render_next_steps(self, request, workflow, start, end):
        """render next steps

        this allows change form content on the fly

        """
        rendered = {}

        request = copy.copy(self.request)
        # patch request method, because we want render new form without
        # validation
        request.method = "GET"

        new_workflow = self.get_workflow_class()(
            request,
            context_seed=workflow.context,
            entry_point=workflow.entry_point)

        for step in new_workflow.steps[end:]:
            rendered[step.get_id()] = step.render()

        return rendered

    def post(self, request, *args, **kwargs):
        """Handler for HTTP POST requests."""
        context = self.get_context_data(**kwargs)
        workflow = context[self.context_object_name]
        try:
            # Check for the VALIDATE_STEP* headers, if they are present
            # and valid integers, return validation results as JSON,
            # otherwise proceed normally.
            validate_step_start = int(self.request.META.get(
                'HTTP_X_HORIZON_VALIDATE_STEP_START', ''))
            validate_step_end = int(self.request.META.get(
                'HTTP_X_HORIZON_VALIDATE_STEP_END', ''))
        except ValueError:
            # No VALIDATE_STEP* headers, or invalid values. Just proceed
            # with normal workflow handling for POSTs.
            pass
        else:
            # There are valid VALIDATE_STEP* headers, so only do validation
            # for the specified steps and return results.
            data = self.validate_steps(request, workflow,
                                       validate_step_start,
                                       validate_step_end)

            next_steps = self.render_next_steps(request, workflow,
                                                validate_step_start,
                                                validate_step_end)
            # append rendered next steps
            data["rendered"] = next_steps

            return http.HttpResponse(json.dumps(data),
                                     content_type="application/json")

        if not workflow.is_valid():
            return self.render_to_response(context)
        try:
            success = workflow.finalize()
        except forms.ValidationError:
            return self.render_to_response(context)
        except Exception:
            success = False
            horizon_exc.handle(request)
        if success:
            msg = workflow.format_status_message(workflow.success_message)
            messages.success(request, msg)
        else:
            msg = workflow.format_status_message(workflow.failure_message)
            messages.error(request, msg)
        if "HTTP_X_HORIZON_ADD_TO_FIELD" in self.request.META:
            field_id = self.request.META["HTTP_X_HORIZON_ADD_TO_FIELD"]
            response = http.HttpResponse()
            if workflow.object:
                data = [self.get_object_id(workflow.object),
                        self.get_object_display(workflow.object)]
                response.content = json.dumps(data)
                response["X-Horizon-Add-To-Field"] = field_id
            return response
        next_url = self.request.POST.get(workflow.redirect_param_name)
        return shortcuts.redirect(next_url or workflow.get_success_url())
