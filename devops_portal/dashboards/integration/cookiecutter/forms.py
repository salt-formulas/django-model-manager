import copy
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


class FieldGeneratorMixin(object):

    FIELDS = {
        "TEXT": {
            "class": CharField,
            "args": tuple(),
            "kwargs": {
                "max_length": 255,
                "label": "",
                "required": True,
                "help_text": ""
            }
        },
        "IP": {
            "class": IPField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "required": True,
                "mask": True
            }
        },
        "BOOL": {
            "class": BooleanField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "required": False
            }
        },
        "CHOICE": {
            "class": ChoiceField,
            "args": tuple(),
            "kwargs": {
                "label": "",
                "choices": [],
                "required": False
            }
        }
    }

    @staticmethod
    def deslugify(string):
        return str(string).replace('_', ' ').capitalize()

    def generate_fields(self, ctx):
        # iterate over fieldsets in context data
        for fieldset in ctx:
            fieldset_name = fieldset.get('name')
            fieldset_label = fieldset.get('label')
            fields = fieldset.get('fields')
            # create fieldset
            self.fields["fieldset_" + fieldset_name] = Fieldset(
                name=fieldset_name,
                label=fieldset_label
            )
            # iterate over fields dictionary
            for field in fields:
                # get field schema from FIELDS and set params
                field_templates = copy.deepcopy(self.FIELDS)
                field_template = field_templates[field['type']]
                field_cls = field_template['class']
                field_args = field_template['args']
                field_kw = field_template['kwargs']
                # set kwargs
                field_kw['fieldset'] = fieldset_name
                field_kw['label'] = field.get('label', None) if 'label' in field else self.deslugify(field['name'])
                field_kw['help_text'] = field.get('help_text', None)
                field_kw['initial'] = field.get('initial', None)
                if 'CHOICE' in field['type']:
                    field_kw['choices'] = field['choices']
                # declare field on self
                self.fields[field['name']] = field_cls(*field_args, **field_kw)
                                
