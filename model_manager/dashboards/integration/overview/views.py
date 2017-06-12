import json
import logging

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from horizon import tables

from .tables import OverviewTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = OverviewTable
    template_name = "integration/overview/index.html"
    page_title = _("Overview")

    def get_data(self):
        return {}


class StatusView(TemplateView):
    template_name = ""

    def get(self, request, *args, **kwargs):
        ret = {
            'series': self.request,
            'settings': {}
        }

        return HttpResponse(json.dumps(ret),
                            content_type='application/json')

