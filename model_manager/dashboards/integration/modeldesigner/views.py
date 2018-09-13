from __future__ import print_function

import logging

from model_manager.api.jenkins import jenkins_client
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon import tabs
from horizon import workflows
from urllib import urlencode

from .forms import VersionForm
from .tables import CookiecutterTable, STATUS_CHOICES
from .tabs import DetailTabGroup
from .utils import AsyncWorkflowView
from .workflows import CreateCookiecutterContext

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CookiecutterTable
    template_name = 'integration/modeldesigner/index.html'
    page_title = _('Model Designer')

    def get_data(self):
        job_id = getattr(settings, 'COOKIECUTTER_JENKINS_JOB')
        try:
            info = jenkins_client.get_job_info(job_id, depth=1)
            builds = info.get('builds', [])
            for build in builds:
                if 'result' not in build:
                    build['result'] = 'UNKNOWN'
                elif build['result'] is None:
                    build['result'] = 'BUILDING'
                if build['result'] not in [chc[0] for chc in STATUS_CHOICES]:
                    build['result'] = 'UNKNOWN'
        except Exception as e:
            msg = 'Unable to connect to Jenkins API.'
            messages.error(self.request, msg)
            LOG.error('Unable to get build history from Jenkins: %s' % repr(e))
            builds = []

        return builds


class ContextVersionView(forms.ModalFormView):
    form_class = VersionForm
    template_name = 'integration/modeldesigner/version.html'
    modal_id = 'context_version_modal'
    modal_header = _('Choose Context Version')
    submit_label = _('Continue')
    submit_url = reverse_lazy('horizon:integration:modeldesigner:version')

    def get_success_url(self, **kwargs):
        form = self.get_form()
        version = form.data['version']
        param = {'version': version}
        url = reverse_lazy('horizon:integration:modeldesigner:create') + '?' + urlencode(param)
        return url


class CreateView(AsyncWorkflowView):
    workflow_class = CreateCookiecutterContext
    template_name = 'integration/modeldesigner/workflow/_workflow_base.html'


class DetailView(tabs.TabView):
    tab_group_class = DetailTabGroup
    template_name = 'integration/modeldesigner/_detail.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(DetailView, self).get_context_data(*args, **kwargs)
        job_id = kwargs.get('job_id', None)
        build_id = kwargs.get('build_id', None)
        title = None
        if job_id and build_id:
            title = jenkins_client.get_build_info(job_id, int(build_id), depth=1)['fullDisplayName']

        ctx['title'] = title

        return ctx
