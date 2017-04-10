from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from horizon import workflows

from .actions import ClusterBasicAction, ClusterServiceAction


class ClusterBasicStep(workflows.Step):
    action_class = ClusterBasicAction
    contributes = ("cluster_name", "cluster_domain")


class ClusterServiceStep(workflows.Step):
    action_class = ClusterServiceAction
    depends_on = ("cluster_name", )
    contributes = ("install_cicd", "install_openstack", "install_opencontrail",
                   "install_kubernetes")


class CreateCookiecutterContext(workflows.Workflow):
    name = _("Create Cookiecutter Context")
    slug = "create_cookiecutter_context"
    wizard = True
    default_steps = (ClusterBasicStep, ClusterServiceStep)
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

