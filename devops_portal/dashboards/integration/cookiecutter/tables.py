
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
# from horizon_contrib.tables import FilterAction


class CreateCookiecutter(tables.LinkAction):
    name = "create_cookiecutter"
    verbose_name = _("Create Cookiecutter")
    url = "horizon:integration:cookiecutter:create"
    #classes = ["ajax-modal"]

    def get_link_url(self, datum=None):
        return reverse(self.url)

#    def allowed(self, request, instance):
#        return request.user.is_manager


class CookiecutterTable(tables.DataTable):

    id = tables.Column("id", verbose_name=_('id'))
    name = tables.Column("name", verbose_name=_('Name'))

    def get_object_id(self, obj):
        return obj.get("id")

    class Meta:
        name = _("Cookiecutter")
        verbose_name = _("Cookiecutters")
        table_actions = (CreateCookiecutter,)
