import yaml

from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import STEP1_CTX, STEP2_CTX, STEP3_CTX
from .utils import GeneratedAction


class GeneralParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP1_CTX

    class Meta(object):
        name = _("General cluster paramaters")


class InfraParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP2_CTX

    class Meta(object):
        name = _("Cluster infrastructure parameters")


class ProductParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP3_CTX

    class Meta(object):
        name = _("Service specific cluster parameters")


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
        cookiecutter_ctx = {'default_context': {k: v for (k, v) in context.items() if v}}
        yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar
        self.fields['cookiecutter_context'].initial = yaml.safe_dump(cookiecutter_ctx, default_flow_style=False)

    class Meta(object):
        name = _("Cookiecutter context")

