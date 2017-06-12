
from django import shortcuts
import django.views.decorators.vary
from django.core.urlresolvers import reverse_lazy

HOME = reverse_lazy('horizon:integration:modeldesigner:index')


def get_user_home(user):
    response = shortcuts.redirect(HOME)
    return response


@django.views.decorators.vary.vary_on_cookie
def splash(request):

    response = shortcuts.redirect(HOME)
    return response

