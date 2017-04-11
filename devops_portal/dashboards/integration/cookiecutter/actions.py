from django.utils.translation import ugettext_lazy as _
from django import forms
from horizon import workflows, forms as horizon_forms


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
        self.fieldset = kwargs.pop('fieldset')
        super(CharField, self).__init__(*args, **kwargs)


class BooleanField(forms.BooleanField):
    """
    Custom BooleanField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        self.fieldset = kwargs.pop('fieldset')
        super(BooleanField, self).__init__(*args, **kwargs)


class IPField(horizon_forms.IPField):
    """
    Custom IPField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        self.fieldset = kwargs.pop('fieldset')
        super(IPField, self).__init__(*args, **kwargs)


class ChoiceField(forms.ChoiceField):
    """
    Custom ThemableChoiceField with fieldset attribute
    """
    def __init__(self, *args, **kwargs):
        self.fieldset = kwargs.pop('fieldset')
        super(ChoiceField, self).__init__(*args, **kwargs)


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

    public_host = CharField(label=_("Public Host"),
                            required=True,
                            initial="${_param:openstack_proxy_address}",
                            fieldset="base")

    public_port = CharField(max_length=255,
                            label=_("Public Port"),
                            initial="https",
                            required=True,
                            fieldset="base")

    fieldset_salt = Fieldset(name="salt", label=_("Salt Master"))

    salt_master_source_choices = [('pkg', _('Package')),
                                  ('git', _('Git'))]

    salt_master_source = ChoiceField(choices = salt_master_source_choices,
                                             label = "Salt Master Source",
                                             required=True,
                                             fieldset="salt")

    reclass_repository = CharField(max_length=255,
                                   label = "Reclass Repository",
                                   initial="git@github.com:Mirantis/reclass-system-salt-model.git",
                                   required=True,
                                   fieldset="salt")

    reclass_branch = CharField(max_length=255,
                               label = "Reclass Branch",
                               initial="master",
                               required=True,
                               fieldset="salt")

    def __init__(self, request, context, *args, **kwargs):
        super(ClusterBasicAction, self).__init__(
            request, context, *args, **kwargs)

        self.help_text = str(context)

    class Meta(object):
        name = _("Basic Cluster Setup")


class ClusterServiceAction(workflows.Action):
    """
    TODO: document this action
    """
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

        self.help_text = str(context)

    class Meta(object):
        name = _("Required Cluster Services")


class ClusterParamsAction(workflows.Action):
    """
    TODO: document this action
    """
    dummy = forms.BooleanField(label=_("Dummy"),
                               help_text="",
                               required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(ClusterParamsAction, self).__init__(
            request, context, *args, **kwargs)

        self.help_text = str(context)

    class Meta(object):
        name = _("Cluster Parameters")

