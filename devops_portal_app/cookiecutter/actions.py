from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows


class ClusterBasicAction(workflows.Action):
    # The name field will be automatically available in all action's
    # methods.
    # If we want this field to be used in the another Step or Workflow,
    # it has to be contributed by this step, then depend on in another
    # step.
    cluster_name = forms.CharField(max_length=255,
                                   label=_("Cluster Name"),
                                   help_text="",
                                   required=True)

    cluster_domain = forms.CharField(max_length=255,
                                     label=_("Cluster Domain"),
                                     help_text="",
                                     required=True)

    def handle(self, request, data):
        pass
