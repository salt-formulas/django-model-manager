from django import http
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from devops_portal.api import devops_portal
from horizon import exceptions
from horizon.utils import functions as utils
#from openstack_dashboard.dashboards.settings.password import forms


@sensitive_variables('data')
def handle(self, request, data):
    """
    just override standard OpenStack-Keystone behavior
    """

    # TODO override change password form
    data.pop('current_password')
    data.pop('confirm_password')

    try:
        devops_portal.users.update_own_password(
            request.user.id,
            data,
            request)
        response = http.HttpResponseRedirect(settings.LOGOUT_URL)
        msg = _("Password changed. Please log in again to continue.")
        utils.add_logout_reason(request, response, msg)
        return response
    except Exception:
        exceptions.handle(request,
                          _('Unable to change password.'))
        return False

#forms.PasswordForm.handle = handle
