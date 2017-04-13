from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import STEP1_CTX, STEP2_CTX, STEP3_CTX
from .utils import GeneratedAction


class ClusterBasicAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP1_CTX

    class Meta(object):
        name = _("Basic Cluster Setup")


class ClusterServiceAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP2_CTX

    class Meta(object):
        name = _("Required Cluster Services")


class ClusterParamsAction(GeneratedAction):
    """
    TODO: document this action
    """
    source_context = STEP3_CTX

    class Meta(object):
        name = _("Cluster Parameters")

