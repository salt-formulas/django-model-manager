import logging
import math
from datetime import date, datetime
from urllib import urlencode

from django.conf import settings
from django.utils import six
from horizon import messages
from horizon_contrib.api import PaginatedManager

LOG = logging.getLogger(__name__)

TOKEN_FORMAT = "  Token {0}"


class BaseClient(PaginatedManager):

    def set_api(self):
        self.api = '%s://%s:%s%s' % (
            getattr(settings, "AUTH_BACKEND_PROTOCOL", "http"),
            getattr(settings, "AUTH_BACKEND_HOST", "127.0.0.1"),
            getattr(settings, "AUTH_BACKEND_PORT", 8001),
            getattr(settings, "AUTH_BACKEND_API_PREFIX", "/api"))

    def process_headers(self, headers, request):
        '''add extra headers'''

        try:
            token = request.session['token'].id
            headers["Authorization"] = TOKEN_FORMAT.format(token)
        except:
            pass

        return headers

    def process_params(self, params, request):
        for key in params.keys():
            value = params[key]
            if isinstance(value, date):
                params[key] = value.strftime('%Y-%m-%d')
        return params
