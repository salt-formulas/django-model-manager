from devops_portal.api.jenkins import jenkins_client
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from horizon import workflows
from time import sleep

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
    name = _("Create Model")
    slug = "create_cookiecutter_context"
    async_wizard = True
    default_steps = (GeneralParamsStep, InfraParamsStep, ProductParamsStep, CookiecutterContextStep)
    finalize_button_name = _("Confirm")
    success_message = _('Your request was successfully submitted.')
    failure_message = _('Your request could not be submitted, please try again later.')
    success_url = "horizon:integration:modeldesigner:index"

    def __init__(self, *args, **kwargs):
        super(CreateCookiecutterContext, self).__init__(*args, **kwargs)
        # contribute choice field options to workflow context as Bools
        context = self.context
        for step in self.steps:
            choice_fields = [obj for obj in step.action.fields.values() if hasattr(obj, 'choices') and getattr(obj, 'extend_context', False)]
            choices = [chc[0] for fld in choice_fields for chc in fld.choices]
            for choice in choices:
                if choice not in context.keys():
                    context[choice] = True if choice in context.values() else False

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

        result = jenkins_client.build_wf(job_name, job_ctx)
        if result:
            # this can delay result for 4, 7 or 10 seconds, but it will attempt
            # to load the overview page after the job started, so it can poll
            # the job status using Horizon async row functionality
            sleep(1)
            for idx in [1, 2, 3]:
                info = jenkins_client.get_job_info(job_name)
                if info.get('inQueue', False):
                    return result
                else:
                    sleep(3)

        return result

