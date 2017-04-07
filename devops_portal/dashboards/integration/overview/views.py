import json
import logging
from horizon import views
from django.views.generic import TemplateView
from django.http import HttpResponse

LOG = logging.getLogger(__name__)


class IndexView(views.HorizonTemplateView):
    template_name = "integration/overview/_index.html"


class StatusView(TemplateView):
    template_name = ""

    def get(self, request, *args, **kwargs):
        ret = {
            'series': self.request,
            'settings': {}
        }

        return HttpResponse(json.dumps(ret),
                            content_type='application/json')
