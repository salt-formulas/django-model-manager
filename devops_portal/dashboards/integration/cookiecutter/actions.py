from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows


class ClusterBasicAction(workflows.Action):
    """
    TODO: document this action
    """
    cluster_name = forms.CharField(max_length=255,
                                   label=_("Cluster Name"),
                                   help_text="",
                                   required=True)

    cluster_domain = forms.CharField(max_length=255,
                                     label=_("Cluster Domain"),
                                     help_text="",
                                     required=True)

    class Meta(object):
        name = _("Cluster Basic Action")


class ClusterServiceAction(workflows.Action):
    """
    TODO: document this action
    """
    install_cicd = forms.BooleanField(label=_("Install CI/CD"),
                                      help_text="",
                                      required=False)

    install_openstack = forms.BooleanField(label=_("Install OpenStack"),
                                           help_text="",
                                           required=False)

    install_opencontrail = forms.BooleanField(label=_("Install OpenContrail"),
                                              help_text="",
                                              required=False)

    install_kubernetes = forms.BooleanField(label=_("Install Kubernetes"),
                                            help_text="",
                                            required=False)

    class Meta(object):
        name = _("Cluster Service Action")

