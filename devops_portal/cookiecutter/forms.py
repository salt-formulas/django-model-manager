import json
import logging

from devops_portal import api
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from horizon import exceptions, forms, messages

LOG = logging.getLogger(__name__)


class CreateCookiecutterForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Create Cookiecutter')
        help_text = _('Generate new Cookiecutter.')

    name = forms.CharField(
        required=True)

    param1 = forms.BooleanField(
        required=False,
        initial=False)

    def handle(self, request, data):

        try:
            api.devops_portal.jobs.create(
                data,
                request)
        except Exception as e:
            raise e

        return True
