import yaml

from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import CTX
from .utils import GeneratedAction


class GeneralParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = CTX

    class Meta(object):
        name = _("General parameters")
        slug = "general_params_action"


class InfraParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = CTX

    class Meta(object):
        name = _("Infrastructure parameters")
        slug = "infra_params_action"


class ProductParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = CTX

    class Meta(object):
        name = _("Product parameters")
        slug = "product_params_action"


def should_use_block(value):
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def my_represent_scalar(self, tag, value, style=None):
    if style is None:
        if should_use_block(value):
             style='|'
             value = value.replace('\r', '')
        else:
            style = self.default_style

    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node


class CookiecutterContextAction(workflows.Action):
    """
    TODO: document this action
    """
    cookiecutter_context = forms.CharField(widget=forms.Textarea(attrs={'rows': '40'}))

    def __init__(self, request, context, *args, **kwargs):
        super(CookiecutterContextAction, self).__init__(
            request, context, *args, **kwargs)
        cookiecutter_ctx = {'default_context': {k: v for (k, v) in context.items() if v is not None and k != 'cookiecutter_context'}}
        transform_bools = {k: str(v).lower() for (k, v) in cookiecutter_ctx['default_context'].items() if isinstance(v, bool)}
        cookiecutter_ctx['default_context'].update(transform_bools)
        yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar
        self.fields['cookiecutter_context'].initial = yaml.safe_dump(cookiecutter_ctx, default_flow_style=False)
        # TODO: this basically makes the field uneditable, but it is necessary to deliver correct initial value
        self.initial['cookiecutter_context'] = self.fields['cookiecutter_context'].initial

    class Meta(object):
        name = _("Output summary")

