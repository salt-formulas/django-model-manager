STEP1_CTX = '''
- name: "base"
  label: "Base"
  step: 1
  fields:
    - name: "cluster_name"
      type: "TEXT"
      help_text: "Name of your cluster"
      initial: "deployment_name"
    - name: "cluster_domain"
      type: "TEXT"
      initial: "deploy-name.local"
    - name: "public_host"
      type: "TEXT"
      initial: "${_param:openstack_proxy_address}"
    - name: "reclass_repository"
      type: "TEXT"
      initial: "https://github.com/Mirantis/mk-lab-salt-model.git"
- name: "services"
  label: "Services"
  step: 1
  fields:
    - name: "platform"
      type: "CHOICE"
      choices:
          - - "openstack_enabled"
            - "OpenStack"
          - - "kubernetes_enabled"
            - "Kubernetes"
      initial: "openstack_enabled"
    - name: "stacklight_enabled"
      type: "BOOL"
      initial: True
    - name: "cicd_enabled"
      type: "BOOL"
      initial: True
- name: "networking"
  label: "Networking"
  step: 1
  fields:
    - name: "dns_server01"
      type: "IP"
      initial: "8.8.8.8"
    - name: "dns_server02"
      type: "IP"
      initial: "8.8.4.4"
    - name: "deploy_network_netmask"
      type: IP
      initial: "255.255.255.0"
    - name: "deploy_network_subnet"
      type: IP
      initial: "10.0.0.0"
    - name: "deploy_network_gateway"
      type: IP
      initial: "10.0.0.1"
    - name: "control_network_subnet"
      type: IP
      initial: "10.0.1.0"
    - name: "control_network_netmask"
      type: IP
      initial: "255.255.255.0"
    - name: "tenant_network_subnet"
      type: IP
      initial: "10.0.2.0"
    - name: "tenant_network_netmask"
      type: IP
      initial: "255.255.255.0"
    - name: "control_vlan"
      type: IP
      initial: "10"
      label: "Control VLAN"
    - name: "tenant_vlan"
      type: IP
      initial: "20"
'''

STEP2_CTX = '''
- name: "salt"
  label: "Salt Master"
  step: 1
  fields:
    - name: "salt_master_address"
      type: "IP"
      initial: "10.167.4.90"
    - name: "salt_master_management_address"
      type: "IP"
      initial: "10.167.5.90"
    - name: "salt_master_hostname"
      type: "TEXT"
      initial: "cfg01"
- name: "openstack_networking"
  label: "OpenStack Networking"
  step: 1
  requires:
    - openstack_enabled: True
  fields:
    - name: "openstack_network_engine"
      type: "CHOICE"
      choices:
        - - "opencontrail"
          - "OpenContrail"
        - - "ovs"
          - "Neutron OVS"

'''

STEP3_CTX = '''
- name: "ovs"
  label: "Neutron OVS"
  step: 1
  requires:
    - openstack_network_engine: ovs
  fields:
    - name: "openstack_ovs_dvr_enabled"
      type: "BOOL"
      initial: False
    - name: "openstack_ovs_encapsulation_type"
      type: "TEXT"
      initial: "vxlan"
    - name: "openstack_ovs_encapsulation_vlan_range"
      type: "TEXT"
      initial: "2416:2420"
'''

