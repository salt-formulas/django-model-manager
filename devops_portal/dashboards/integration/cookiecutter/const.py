
STEP1_CTX = '''
base:
  label: "Base"
  step: 1
  fields:
    cluster_name:
      type: "TEXT"
      description: "Name of your cluster"
      initial: "deployment_name"
    cluster_domain:
      type: "TEXT"
      initial: "deploy-name.local"
    public_host:
      type: "TEXT"
      initial: "${_param:openstack_proxy_address}"
    reclass_repository:
      type: "TEXT"
      initial: "https://github.com/Mirantis/mk-lab-salt-model.git"
services:
  label: "Services"
  step: 1
  fields:
    openstack_enabled:
      type: "BOOL"
      initial: True
    stacklight_enabled:
      type: "BOOL"
      initial: True
    cicd_enabled:
      type: "BOOL"
      initial: True
    kubernetes_enabled:
      type: "BOOL"
      initial: False
networking:
  label: "Networking"
  step: 1
  fields:
    dns_server01:
      type: IP
      initial: "8.8.8.8"
    dns_server02:
      type: IP
      initial: "8.8.4.4"
    deploy_network_netmask:
      type: IP
      initial: "255.255.255.0"
    deploy_network_subnet:
      type: IP
      initial: "10.0.0.0"
    deploy_network_gateway:
      type: IP
    control_network_subnet:
      type: IP
      initial: "10.0.1.0"
    control_network_netmask:
      type: IP
      initial: "255.255.255.0"
    tenant_network_subnet:
      type: IP
      initial: "10.0.2.0"
    tenant_network_netmask:
      type: IP
      initial: "255.255.255.0"
    control_vlan:
      type: IP
      initial: "10"
    tenant_vlan:
      type: IP
      initial: "20"
'''

