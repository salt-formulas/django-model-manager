from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
# from horizon_contrib.tables import FilterAction


class ShowDetail(tables.LinkAction):

    name = 'show_detail'
    verbose_name = _("View detail")
    url = 'horizon:integration:cookiecutter:detail'

    def get_link_url(self, datum):
        return reverse(self.url, args=[datum['number']])


class CreateCookiecutter(tables.LinkAction):
    name = "create_cookiecutter"
    verbose_name = _("Create Cookiecutter")
    url = "horizon:integration:cookiecutter:create"

    def get_link_url(self, datum=None):
        return reverse(self.url)


class BuildTableBase(tables.DataTable):

    def get_object_id(self, datum):
        return datum["number"]


class CookiecutterTable(BuildTableBase):

    number = tables.Column('number', verbose_name=_("Number"))
    url = tables.Column('url', verbose_name=_("Url"))
    result = tables.Column('result', verbose_name=_("Result"))

    class Meta:
        name = _("Cookiecutter")
        verbose_name = _("Cookiecutters")
        table_actions = (CreateCookiecutter,)
        #row_actions = (ShowDetail,)

