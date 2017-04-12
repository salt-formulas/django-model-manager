from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows

from .const import STEP1_CTX
from .forms import Fieldset, CharField, BooleanField, IPField, ChoiceField


class ClusterBasicAction(workflows.Action):
    """
    TODO: document this action
    """
    fieldset_base = Fieldset(name="base", label=_("Base"))

    cluster_name = CharField(max_length=255,
                             label=_("Cluster Name"),
                             initial="deployment_name",
                             required=True,
                             fieldset="base")

    cluster_domain = CharField(max_length=255,
                               label=_("Cluster Domain"),
                               initial="deploy-name.local",
                               required=True,
                               fieldset="base")

    public_host = CharField(max_length=255,
                            label=_("Public Host"),
                            required=True,
                            initial="${_param:openstack_proxy_address}",
                            fieldset="base")

    reclass_repository = CharField(max_length=255,
                                   label = "Reclass Repository",
                                   initial="https://github.com/Mirantis/mk-lab-salt-model.git",
                                   required=True,
                                   fieldset="base")

    fieldset_services = Fieldset(name="services", label=_("Services"))

    install_cicd = BooleanField(label=_("Install CI/CD"),
                                fieldset="services",
                                required=False)

    install_openstack = BooleanField(label=_("Install OpenStack"),
                                     fieldset="services",
                                     required=False)

    install_opencontrail = BooleanField(label=_("Install OpenContrail"),
                                        fieldset="services",
                                        required=False)

    install_stacklight = BooleanField(label=_("Install StackLight"),
                                      fieldset="services",
                                      required=False)

    install_kubernetes = BooleanField(label=_("Install Kubernetes"),
                                      fieldset="services",
                                      required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(ClusterBasicAction, self).__init__(
            request, context, *args, **kwargs)

    class Meta(object):
        name = _("Basic Cluster Setup")


class ClusterServiceAction(workflows.Action):
    """
    TODO: document this action
    """
    fieldset_networking = Fieldset(name="networking", label=_("Networking"))

    pxe_subnet = IPField(label = "PXE Subnet",
                         initial = "192.168.1.0/24",
                         mask=True,
                         required=True,
                         fieldset="networking")

    pxe_router = IPField(label = "PXE Router",
                         initial = "192.168.1.1",
                         mask=True,
                         required=True,
                         fieldset="networking")

    def __init__(self, request, context, *args, **kwargs):
        super(ClusterServiceAction, self).__init__(
            request, context, *args, **kwargs)

    class Meta(object):
        name = _("Required Cluster Services")


from .forms import FieldGeneratorMixin
from .utils import generate_context, INFRA_JSON_URL

class ClusterParamsAction(workflows.Action, FieldGeneratorMixin):
    """
    TODO: document this action
    """
    def __init__(self, request, context, *args, **kwargs):
        super(ClusterParamsAction, self).__init__(
            request, context, *args, **kwargs)

        ctx_infra = generate_context('github', 'infra', 'Infra', **{'url': INFRA_JSON_URL})
        self.generate_fields(ctx_infra)

    class Meta(object):
        name = _("Cluster Parameters")

