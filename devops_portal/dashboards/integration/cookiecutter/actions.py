import yaml

from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import STEP1_CTX, STEP2_CTX, STEP3_CTX
from .utils import GeneratedAction


class ClusterBasicAction(GeneratedAction):
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


class ClusterServiceAction(GeneratedAction):
    """
    TODO: document this action
    """
    def __init__(self, request, context, *args, **kwargs):
        super(ClusterServiceAction, self).__init__(
            request, context, *args, **kwargs)

        ctx = yaml.load(STEP2_CTX)
        self.generate_fields(ctx)

    class Meta(object):
        name = _("Required Cluster Services")


class ClusterParamsAction(GeneratedAction):
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

