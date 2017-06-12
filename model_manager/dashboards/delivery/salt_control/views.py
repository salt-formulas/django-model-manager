import logging

from django.utils.translation import ugettext_lazy as _

from horizon.views import HorizonTemplateView

LOG = logging.getLogger(__name__)


class IndexView(HorizonTemplateView):
    template_name = "delivery/salt_control/index.html"
    page_title = _("Salt Minion Control")

    def get_data(self):
        return {}
