from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from horizon import workflows

from .actions import (GeneralParamsAction, InfraParamsAction, ProductParamsAction,
    CookiecutterContextAction)
from .const import STEP1_CTX, STEP2_CTX, STEP3_CTX
from .utils import GeneratedStep


class GeneralParamsStep(GeneratedStep):
    action_class = GeneralParamsAction
    source_context = STEP1_CTX


class InfraParamsStep(GeneratedStep):
    action_class = InfraParamsAction
    source_context = STEP2_CTX


class ProductParamsStep(GeneratedStep):
    action_class = ProductParamsAction
    source_context = STEP3_CTX


class CookiecutterContextStep(workflows.Step):
    action_class = CookiecutterContextAction


class CreateCookiecutterContext(workflows.Workflow):
    name = _("Create Cookiecutter Context")
    slug = "create_cookiecutter_context"
    async_wizard = True
    default_steps = (GeneralParamsStep, InfraParamsStep, ProductParamsStep, CookiecutterContextStep)
    finalize_button_name = _("Confirm")
    success_message = _('Your request was successfully submitted.')
    failure_message = _('Your request could not be submitted, please try again later.')

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
        return True

