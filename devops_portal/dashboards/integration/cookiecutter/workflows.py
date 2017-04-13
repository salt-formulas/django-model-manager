import yaml

from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from horizon import workflows

from .actions import ClusterBasicAction, ClusterServiceAction, ClusterParamsAction
from .const import STEP1_CTX, STEP2_CTX
from .utils import GeneratedStep


class ClusterBasicStep(GeneratedStep):
    action_class = ClusterBasicAction
    template_name = "integration/cookiecutter/workflow/_workflow_step_with_fieldsets.html"
    depends_on = tuple()
    contributes = tuple()
    source_context = yaml.load(STEP1_CTX)


class ClusterServiceStep(GeneratedStep):
    action_class = ClusterServiceAction
    template_name = "integration/cookiecutter/workflow/_workflow_step_with_fieldsets.html"
    depends_on = tuple()
    contributes = tuple()
    source_context = yaml.load(STEP2_CTX)


class ClusterParamsStep(GeneratedStep):
    action_class = ClusterParamsAction
    template_name = "integration/cookiecutter/workflow/_workflow_step_with_fieldsets.html"
    depends_on = tuple()
    contributes = tuple()


class CreateCookiecutterContext(workflows.Workflow):
    name = _("Create Cookiecutter Context")
    slug = "create_cookiecutter_context"
    wizard = True
    default_steps = (ClusterBasicStep, ClusterServiceStep, ClusterParamsStep)
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

    def handle(self, request, data):
        pass

