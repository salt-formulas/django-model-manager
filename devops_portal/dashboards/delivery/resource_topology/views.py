import logging

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from horizon.views import HorizonTemplateView

LOG = logging.getLogger(__name__)


class IndexView(HorizonTemplateView):
    template_name = "delivery/resource_topology/index.html"
    page_title = _("Resource Topology")

    def get_data(self):
        return {}


def topology_data_view(self, *args, **kwargs):
    data = {
        'test_dict': {
            'my_key': 'my_value'
        }
    }

    return JsonResponse(data)

