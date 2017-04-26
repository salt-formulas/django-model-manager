from __future__ import print_function

import logging

from devops_portal.api.jenkins import jenkins_client
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon import workflows

from .tables import CookiecutterTable
from .tabs import DetailTabGroup
from .utils import AsyncWorkflowView
from .workflows import CreateCookiecutterContext

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CookiecutterTable
    template_name = 'integration/cookiecutter/index.html'
    page_title = _('Cookiecutters')

    def get_data(self):
        job_id = getattr(settings, 'COOKIECUTTER_JENKINS_JOB')
        return jenkins_client.get_builds(job_id)


class CreateView(AsyncWorkflowView):
    workflow_class = CreateCookiecutterContext
    template_name = 'integration/cookiecutter/workflow/_workflow_base.html'


class DetailView(tabs.TabView):
    tab_group_class = DetailTabGroup
    template_name = 'integration/cookiecutter/_detail.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(DetailView, self).get_context_data(*args, **kwargs)
        job_id = kwargs.get('job_id', None)
        build_id = kwargs.get('build_id', None)
        title = None
        if job_id and build_id:
            title = jenkins_client.get_build_info(job_id, int(build_id), depth=1)['fullDisplayName']

        ctx['title'] = title

        return ctx

