import json
import logging

#from model_manager import api
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
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


class FieldMixin(object):
    """
    Mixin extending custom fields
    """
    def __init__(self, *args, **kwargs):
        if 'width' in kwargs:
            width = kwargs.pop('width')
            self.width = width if width in ['full', 'half'] else 'full'
        if 'fieldset' in kwargs:
            self.fieldset = kwargs.pop('fieldset')
        super(FieldMixin, self).__init__(*args, **kwargs)


class FileField(FieldMixin, forms.FileField):
    """
    Custom FileField with fieldset attribute
    """
    pass


class CharField(FieldMixin, forms.CharField):
    """
    Custom CharField with fieldset attribute
    """
    pass


class BooleanField(FieldMixin, forms.BooleanField):
    """
    Custom BooleanField with fieldset attribute
    """
    pass


class IPField(FieldMixin, horizon_forms.IPField):
    """
    Custom IPField with fieldset attribute
    """
    pass


class ChoiceField(FieldMixin, forms.ChoiceField):
    """
    Custom ChoiceField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        if 'extend_context' in kwargs:
            self.extend_context = kwargs.pop('extend_context')
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
            api.model_manager.jobs.create(
                data,
                request)
        except Exception as e:
            raise e

        return True


def version_choices():
    from .utils import ContextTemplateCollector
    collector = ContextTemplateCollector()
    versions = collector.collect_versions()
    return [(v, v) for v in versions]


class VersionForm(forms.SelfHandlingForm):
    version = forms.ChoiceField(label='Version', choices=version_choices)

    def handle(self, request, data):
        return True
