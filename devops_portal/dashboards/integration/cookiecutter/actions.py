import yaml

from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import STEP1_CTX, STEP2_CTX, STEP3_CTX
from .forms import FieldGeneratorMixin, Fieldset, CharField, BooleanField, IPField, ChoiceField


class ClusterBasicAction(workflows.Action, FieldGeneratorMixin):
    """
    TODO: document this action
    """
    def __init__(self, request, context, *args, **kwargs):
        super(ClusterBasicAction, self).__init__(
            request, context, *args, **kwargs)

        ctx = yaml.load(STEP1_CTX)
        self.generate_fields(ctx)

    class Meta(object):
        name = _("Basic Cluster Setup")


class ClusterServiceAction(workflows.Action, FieldGeneratorMixin):
    """
    TODO: document this action
    """

    openstack_enabled = forms.BooleanField(widget=forms.HiddenInput(),
                                           initial=False)
    kubernetes_enabled = forms.BooleanField(widget=forms.HiddenInput(),
                                            initial=False)

    def __init__(self, request, context, *args, **kwargs):
        super(ClusterServiceAction, self).__init__(
            request, context, *args, **kwargs)

        ctx = yaml.load(STEP2_CTX)
        self.generate_fields(ctx)

        # add missing parameters openstack_enabled, kubernetes_enabled to context
        # depends on platform select from previous step
        if 'platform' in context:
            platform = context.get('platform')
            if 'openstack_enabled' in platform:
                self.fields['openstack_enabled'].initial = True
            elif 'kubernetes_enabled' in platform:
                self.fields['kubernetes_enabled'].initial = True
                del self.fields['fieldset_openstack_networking']
                del self.fields['openstack_network_engine']

        return

    class Meta(object):
        name = _("Required Cluster Services")


class ClusterParamsAction(workflows.Action, FieldGeneratorMixin):
    """
    TODO: document this action
    """
    def __init__(self, request, context, *args, **kwargs):
        super(ClusterParamsAction, self).__init__(
            request, context, *args, **kwargs)

        ctx = yaml.load(STEP3_CTX)
        self.generate_fields(ctx)

    class Meta(object):
        name = _("Cluster Parameters")

