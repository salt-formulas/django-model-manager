from model_manager.api.jenkins import jenkins_client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from horizon import tables
# from horizon_contrib.tables import FilterAction

STATUS_DISPLAY_CHOICES = (
    ("SUCCESS", pgettext_lazy("Job build status", u"Success")),
    ("FAILURE", pgettext_lazy("Job build status", u"Failure")),
    ("UNKNOWN", pgettext_lazy("Job build status", u"Unknown")),
    ("BUILDING", pgettext_lazy("Job build status", u"Building")),
)

STATUS_CHOICES = ( 
    ("SUCCESS", True),
    ("FAILURE", False),
    ("UNKNOWN", False),
    ("BUILDING", None),
)


class ShowDetail(tables.LinkAction):

    name = 'show_detail'
    verbose_name = _("View detail")
    url = 'horizon:integration:modeldesigner:detail'

    def get_link_url(self, datum):
        return reverse(self.url, args=[datum['number']])


class CreateCookiecutter(tables.LinkAction):
    name = 'create_cookiecutter'
    verbose_name = _('Create Model')
    url = 'horizon:integration:modeldesigner:create'

    def get_link_url(self, datum=None):
        return reverse(self.url)

    def allowed(self, request, datum):
        return not getattr(settings, 'COOKIECUTTER_CONTEXT_VERSIONING_ENABLED', False)


class CreateCookiecutterWithVersion(tables.LinkAction):
    name = 'create_cookiecutter_with_version'
    verbose_name = _('Create Model')
    url = 'horizon:integration:modeldesigner:version'
    classes = ('ajax-modal',)

    def get_link_url(self, datum=None):
        return reverse(self.url)

    def allowed(self, request, datum):
        return getattr(settings, 'COOKIECUTTER_CONTEXT_VERSIONING_ENABLED', False)


class JobRow(tables.Row):

    ajax = True

    def get_data(self, request, id):
        name = getattr(settings, 'COOKIECUTTER_JENKINS_JOB')
        info = jenkins_client.get_build_info(name, int(id))

        return info


class BuildTableBase(tables.DataTable):

    def get_object_id(self, datum):
        return datum["number"]


class CookiecutterTable(BuildTableBase):

    number = tables.Column('number', verbose_name=_("Number"))
    url = tables.Column('url', verbose_name=_("Url"))
    description = tables.Column('description', verbose_name=_("Description"))
    result = tables.Column('result',
                           status=True,
                           status_choices=STATUS_CHOICES,
                           display_choices=STATUS_DISPLAY_CHOICES,
                           verbose_name=_("Status"))

    class Meta:
        name = _("Cookiecutter")
        verbose_name = _("Cookiecutters")
        status_columns = ('result',)
        row_class = JobRow
        table_actions = (CreateCookiecutter, CreateCookiecutterWithVersion)
        #row_actions = (ShowDetail,)

