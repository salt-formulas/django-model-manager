import json
import logging

#from devops_portal import api
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from horizon import exceptions, forms, messages, workflows, forms as horizon_forms

LOG = logging.getLogger(__name__)


class Fieldset(forms.Field):
    """
    Fake field to use in _form_fields_with_fieldsets.html template,
    Fieldset.name connects to Field.fieldset
    """
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self.is_fieldset = True
        kwargs['required'] = False
        super(Fieldset, self).__init__(*args, **kwargs)


class CharField(forms.CharField):
    """
    Custom CharField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("fieldset", None):
            self.fieldset = kwargs.pop('fieldset')
        super(CharField, self).__init__(*args, **kwargs)


class BooleanField(forms.BooleanField):
    """
    Custom BooleanField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("fieldset", None):
            self.fieldset = kwargs.pop('fieldset')
        super(BooleanField, self).__init__(*args, **kwargs)


class IPField(horizon_forms.IPField):
    """
    Custom IPField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("fieldset", None):
            self.fieldset = kwargs.pop('fieldset')
        super(IPField, self).__init__(*args, **kwargs)


class ChoiceField(forms.ChoiceField):
    """
    Custom ThemableChoiceField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("fieldset", None):
            self.fieldset = kwargs.pop('fieldset')
        super(ChoiceField, self).__init__(*args, **kwargs)


class CreateCookiecutterForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Create Cookiecutter')
        help_text = _('Generate new Cookiecutter.')

    name = forms.CharField(
        required=True)

    param1 = forms.BooleanField(
        required=False,
        initial=False)

    def handle(self, request, data):

        try:
            api.devops_portal.jobs.create(
                data,
                request)
        except Exception as e:
            raise e

        return True

