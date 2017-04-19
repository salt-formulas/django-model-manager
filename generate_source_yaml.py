import yaml

from devops_portal.dashboards.integration.cookiecutter.utils import (generate_context,
    INFRA_JSON_URL, CICD_JSON_URL, KUBERNETES_JSON_URL, OPENCONTRAIL_JSON_URL,
    OPENSTACK_JSON_URL, STACKLIGHT_JSON_URL)

infra_ctx = generate_context("github", "infra", "Infra", **{'url': INFRA_JSON_URL})
cicd_ctx = generate_context("github", "cicd", "CI/CD", **{'url': CICD_JSON_URL})
kubernetes_ctx = generate_context("github", "kubernetes", "Kubernetes", **{'url': KUBERNETES_JSON_URL})
opencontrail_ctx = generate_context("github", "opencontrail", "OpenContrail", **{'url': OPENCONTRAIL_JSON_URL})
openstack_ctx = generate_context("github", "openstack", "OpenStack", **{'url': OPENSTACK_JSON_URL})
stacklight_ctx = generate_context("github", "stacklight", "Stacklight", **{'url': STACKLIGHT_JSON_URL})

ctx = infra_ctx + cicd_ctx + kubernetes_ctx + opencontrail_ctx + openstack_ctx + stacklight_ctx

print yaml.safe_dump(ctx, default_flow_style=False)

