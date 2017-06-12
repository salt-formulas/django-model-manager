from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables


class OverviewTable(tables.DataTable):

    id = tables.Column("id", verbose_name=_('id'))
    name = tables.Column("name", verbose_name=_('Name'))

    def get_object_id(self, obj):
        return obj.get("id")

    class Meta:
        name = _("Overview")
        verbose_name = _("Overviews")

