from horizon import workflows

from .actions import ClusterBasicAction, ClusterServiceAction


class ClusterBasicStep(workflows.Step):
    action_class = ClusterBasicAction
#    depends_on = ("has_domain", )
    contributes = ("cluster_name", "cluser_domain")


class ClusterServiceStep(workflows.Step):
    action_class = ClusterServiceAction
    depends_on = ("cluster_name", )
    depends_on = ("install_cicd", "install_openstack", "install_opencontrail",
                  "install_kubernetes")


class CreateCookiecutterContext(workflows.Workflow):

    default_steps = (ClusterBasicStep, ClusterServiceStep)

    def handle(self, request, data):
        pass
