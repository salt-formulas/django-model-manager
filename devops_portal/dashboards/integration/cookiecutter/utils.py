import copy
import json
import requests
import socket

from django import http
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from horizon import workflows

from .forms import Fieldset, CharField, BooleanField, IPField, ChoiceField 

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


class GeneratedAction(workflows.Action):
    source_context = {}
    field_templates = {
        "TEXT": {
            "class": CharField,
            "args": tuple(),
            "kwargs": {
                "max_length": 255,
                "label": "",
                "required": True,
                "help_text": ""
            }
        },
        "IP": {
            "class": IPField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "required": True,
                "mask": True
            }
        },
        "BOOL": {
            "class": BooleanField,
            "args": tuple(),
            "kwargs": {
                "label": "",
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
        }
    }

    def __init__(self, request, context, *args, **kwargs):
        super(GeneratedAction, self).__init__(
            request, context, *args, **kwargs)

        for fieldset in self.source_context:
            skip = False
            if context and 'requires' in fieldset:
                for req in fieldset['requires']:
                    key = req.keys()[0]
                    value = req.values()[0]
                    if (not key in context) or (key in context and not value == context[key]):
                        skip = True
            if skip:
                continue

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
                # get field schema from FIELDS and set params
                field_templates = copy.deepcopy(self.field_templates)
                field_template = field_templates[field['type']]
                field_cls = field_template['class']
                field_args = field_template['args']
                field_kw = field_template['kwargs']
                # set kwargs
                field_kw['fieldset'] = fieldset_name
                field_kw['label'] = field.get('label', None) if 'label' in field else self.deslugify(field['name'])
                field_kw['help_text'] = field.get('help_text', None)
                field_kw['initial'] = field.get('initial', None)
                if 'CHOICE' in field['type']:
                    field_kw['choices'] = field['choices']
                # declare field on self
                self.fields[field['name']] = field_cls(*field_args, **field_kw)

    @staticmethod
    def deslugify(string):
        return str(string).replace('_', ' ').capitalize()


class GeneratedStep(workflows.Step):
    source_context = {}

    def __init__(self, *args, **kwargs):
        super(GeneratedStep, self).__init__(*args, **kwargs)
        ctx = self.source_context
        # get lists of fields
        field_lists = [x['fields'] for x in ctx]
        # flatten the lists
        field_list = [item for sublist in field_lists for item in sublist]
        contributes = list(self.contributes)
        for field in field_list:
            contributes.append(field['name'])
        self.contributes = tuple(contributes)

    def contribute(self, data, context):
        # TODO: Don't call super, override default functionality to
        # contribute all keys in data and remove __init__ override
        super(GeneratedStep, self).contribute(data, context)
        # update shared context with option Bool values according to choices made in ChoiceList fields
        choice_fields = [obj for obj in self.action.fields.values() if hasattr(obj, 'choices')]
        choices = [chc[0] for fld in choice_fields for chc in fld.choices]
        for choice in choices:
            context[choice] = True if choice in context.values() else False
        return context


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
            exceptions.handle(request)
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
