
from __future__ import print_function

import logging

from devops_portal import api
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions, forms, tables

from .forms import CreateCookiecutterForm
from .tables import CookiecutterTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CookiecutterTable
    template_name = 'devops_portal/cookiecutter/index.html'

    def get_data(self):

        try:
            cookiecutters = api.devops_portal.jobs.list(self.request)
        except:
            cookiecutters = []
            exceptions.handle(self.request, _('Unable to load cookiecutters.'))

        return cookiecutters


class CreateView(forms.ModalFormView):
    form_class = CreateCookiecutterForm
    template_name = 'devops_portal/cookiecutter/create.html'
    success_url = reverse_lazy('horizon:devops_portal:cookiecutter:index')
