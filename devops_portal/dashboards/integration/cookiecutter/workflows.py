from devops_portal.api.jenkins import jenkins_client
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from horizon import workflows

from .actions import (GeneralParamsAction, InfraParamsAction, ProductParamsAction,
    CookiecutterContextAction)
from .const import CTX
from .utils import GeneratedStep


class GeneralParamsStep(GeneratedStep):
    action_class = GeneralParamsAction
    source_context = CTX


class InfraParamsStep(GeneratedStep):
    action_class = InfraParamsAction
    source_context = CTX


class ProductParamsStep(GeneratedStep):
    action_class = ProductParamsAction
    source_context = CTX


class CookiecutterContextStep(workflows.Step):
    action_class = CookiecutterContextAction
    contributes = ('cookiecutter_context',)


class CreateCookiecutterContext(workflows.Workflow):
    name = _("Create Cookiecutter Context")
    slug = "create_cookiecutter_context"
    async_wizard = True
    default_steps = (GeneralParamsStep, InfraParamsStep, ProductParamsStep, CookiecutterContextStep)
    finalize_button_name = _("Confirm")
    success_message = _('Your request was successfully submitted.')
    failure_message = _('Your request could not be submitted, please try again later.')

    def __init__(self, *args, **kwargs):
        super(CreateCookiecutterContext, self).__init__(*args, **kwargs)
        # contribute choice field options to workflow context as Bools
        context = self.context
        for step in self.steps:
            choice_fields = [obj for obj in step.action.fields.values() if hasattr(obj, 'choices')]
            choices = [chc[0] for fld in choice_fields for chc in fld.choices]
            for choice in choices:
                if choice not in context.keys():
                    context[choice] = True if choice in context.values() else False

    def get_success_url(self):
        request = self.request
        success_url = None

        if request.method in ("POST", "PUT"):
            referrer = request.META.get('HTTP_REFERER')
            if referrer and is_safe_url(referrer, request.get_host()):
                success_url = referrer

        if not success_url:
            success_url = iri_to_uri(request.get_full_path())

        return success_url

    def handle(self, request, context):
        """Handles any final processing for this workflow. Should return a
        boolean value indicating success.
        """
        job_name = getattr(settings, 'COOKIECUTTER_JENKINS_JOB')
        job_ctx = {
            'COOKIECUTTER_TEMPLATE_BRANCH': 'master',
            'COOKIECUTTER_TEMPLATE_CONTEXT': context.get('cookiecutter_context', {}),
            'COOKIECUTTER_TEMPLATE_CREDENTIALS': 'github-credentials',
            'COOKIECUTTER_TEMPLATE_PATH': './',
            'COOKIECUTTER_TEMPLATE_URL': 'git@github.com:Mirantis/mk2x-cookiecutter-reclass-model.git',
            'EMAIL_ADDRESS': '',
            'RECLASS_MODEL_BRANCH': 'master',
            'RECLASS_MODEL_CREDENTIALS': 'gerrit',
            'RECLASS_MODEL_URL': ''
        }
        for param in job_ctx:
            if param.lower() in context and context.get(param.lower(), None):
                job_ctx[param] = context[param.lower()]

        return jenkins_client.build_wf(job_name, job_ctx)

