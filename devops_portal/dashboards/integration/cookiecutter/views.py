from __future__ import print_function

import logging

#from devops_portal import api
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import workflows

from .tables import CookiecutterTable
from .workflows import CreateCookiecutterContext

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CookiecutterTable
    template_name = "integration/cookiecutter/index.html"
    page_title = _("Cookiecutters")

    def get_data(self):
        try:
            cookiecutters = api.devops_portal.cutter.list(self.request)
        except Exception:
            cookiecutters = []
            exceptions.handle(self.request, _('Unable to load cookiecutters.'))
        return cookiecutters


class CreateView(workflows.WorkflowView):
    workflow_class = CreateCookiecutterContext
