STEP1_CTX = '''
- name: "base"
  label: "Base"
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
    - name: "deployment_type"
      label: "Deployment type"
      type: "CHOICE"
      initial: "physical"
      choices:
          - - "heat"
            - "Heat"
          - - "physical"
            - "Physical"
- name: "services"
  label: "Services"
  fields:
    - name: "platform"
      type: "CHOICE"
      choices:
          - - "openstack_enabled"
            - "OpenStack"
          - - "kubernetes_enabled"
            - "Kubernetes"
      initial: "openstack_enabled"
    - name: "opencontrail_enabled"
      type: "BOOL"
      initial: True
      label: "OpenContrail enabled"
    - name: "stacklight_enabled"
      type: "BOOL"
      initial: True
      label: "StackLight enabled"
    - name: "cicd_enabled"
      type: "BOOL"
      initial: True
      label: "CI/CD enabled"
- name: "networking"
  label: "Networking"
  fields:
    - name: "dns_server01"
      type: "IP"
      initial: "8.8.8.8"
      label: "DNS Server 01"
    - name: "dns_server02"
      type: "IP"
      initial: "8.8.4.4"
      label: "DNS Server 02"
    - name: "deploy_network_subnet"
      type: IP
      initial: "10.0.0.0/24"
      mask: True
    - name: "deploy_network_gateway"
      type: IP
      initial: "10.0.0.1"
    - name: "control_network_subnet"
      type: IP
      initial: "10.0.1.0/24"
      mask: True
    - name: "tenant_network_subnet"
      type: IP
      initial: "10.0.2.0/24"
      mask: True
    - name: "tenant_network_gateway"
      type: IP
      initial: "10.0.2.1"
    - name: "control_vlan"
      type: TEXT
      initial: "10"
      label: "Control VLAN"
    - name: "tenant_vlan"
      type: TEXT
      initial: "20"
      label: "Tenant VLAN"
'''

STEP2_CTX = '''
- name: "salt"
  label: "Salt Master"
  fields:
    - name: "salt_master_address"
      type: "IP"
      initial: {{ control_network_subnet | subnet(90) }}
    - name: "salt_master_management_address"
      type: "IP"
      initial: {{ deploy_network_subnet | subnet(90) }}
    - name: "salt_master_hostname"
      type: "TEXT"
      initial: "cfg01"
    - initial: {{ 32|generate_password }}
      name: salt_api_password
      type: TEXT
      hidden: True
- name: "openstack_networking"
  label: "OpenStack Networking"
  requires:
    - platform: "openstack_enabled"
  fields:
    - name: "openstack_network_engine"
      type: "TEXT"
      initial: "opencontrail"
      readonly: True
      requires:
        - opencontrail_enabled: True
    - name: "openstack_network_engine"
      type: "TEXT"
      initial: "ovs"
      readonly: True
      requires:
        - opencontrail_enabled: False
    - initial: 'False'
      name: openstack_nfv_sriov_enabled
      label: 'OpenStack NFV SRIOV enabled'
      type: BOOL
    - initial: 'False'
      name: openstack_nfv_dpdk_enabled
      type: BOOL
    - initial: 'False'
      name: openstack_nova_compute_nfv_req_enabled
      type: BOOL
'''

STEP3_CTX = '''
{% set private_key, public_key = generate_ssh_keypair() %}
- label: "Infrastructure product parameters"
  name: "infra"
  fields:
  - name: "deploy_network_netmask"
    type: IP
    initial: {{ deploy_network_subnet | netmask }}
    hidden: True
  - name: "control_network_netmask"
    type: IP
    initial: {{ control_network_subnet | netmask }}
    hidden: True
  - name: "tenant_network_netmask"
    type: IP
    initial: {{ tenant_network_subnet | netmask }}
    hidden: True
  - initial: eth2
    name: infra_primary_second_nic
    type: TEXT
    requires:
      - deployment_type: "physical"
  - initial: kvm02
    name: infra_kvm02_hostname
    type: TEXT
    requires:
      - deployment_type: "physical"
  - initial: kvm03
    name: infra_kvm03_hostname
    type: TEXT
    requires:
      - deployment_type: "physical"
  - initial: eth0
    name: infra_deploy_nic
    type: TEXT
    requires:
      - deployment_type: "physical"
  - name: "infra_kvm01_control_address"
    initial: {{ control_network_subnet | subnet(241) }}
    type: "IP"
    requires:
      - deployment_type: "physical"
  - initial: eth1
    name: infra_primary_first_nic
    type: TEXT
    requires:
      - deployment_type: "physical"
  - initial: '100'
    name: openstack_compute_count
    type: TEXT
    requires:
      - platform: "openstack_enabled"
  - initial: kvm01
    name: infra_kvm01_hostname
    type: TEXT
    requires:
      - deployment_type: "physical"
  - name: "infra_kvm_vip_address"
    initial: {{ control_network_subnet | subnet(240) }}
    type: "IP"
    requires:
      - deployment_type: "physical"
  - initial: {{ control_network_subnet | subnet(243) }}
    name: "infra_kvm03_control_address"
    type: "IP"
    requires:
      - deployment_type: "physical"
  - initial: {{ control_network_subnet | subnet(242) }}
    name: infra_kvm02_control_address
    type: IP
    requires:
      - deployment_type: "physical"
  - initial: {{ deploy_network_subnet | subnet(242) }}
    name: infra_kvm02_deploy_address
    type: IP
    requires:
      - deployment_type: "physical"
  - initial: {{ salt_api_password|hash_password }}
    name: salt_api_password_hash
    type: TEXT
    hidden: True
  - initial: {{ deploy_network_subnet | subnet(243) }}
    name: infra_kvm03_deploy_address
    type: IP
    requires:
      - deployment_type: "physical"
  - initial: {{ deploy_network_subnet | subnet(241) }}
    name: infra_kvm01_deploy_address
    type: IP
    requires:
      - deployment_type: "physical"
- label: "CI/CD product parameters"
  name: "cicd"
  requires:
    - cicd_enabled: True
  fields:
  - initial: "{{ private_key }}"
    name: cicd_private_key
    type: LONG_TEXT
    hidden: True
  - initial: cid02
    name: cicd_control_node02_hostname
    type: TEXT
    hidden: True
  - initial: {{ public_key }}
    name: cicd_public_key
    type: LONG_TEXT
  - initial: {{ control_network_subnet | subnet(90) }}
    name: cicd_control_vip_address
    type: IP
  - initial: cid03
    name: cicd_control_node03_hostname
    type: TEXT
  - initial: cid01
    name: cicd_control_node01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(92) }}
    name: cicd_control_node02_address
    type: IP
  - initial: {{ control_network_subnet | subnet(91) }}
    name: cicd_control_node01_address
    type: IP
  - initial: {{ control_network_subnet | subnet(93) }}
    name: cicd_control_node03_address
    type: IP
  - initial: cid
    name: cicd_control_vip_hostname
    type: TEXT
  - initial: 'False'
    name: openldap_enabled
    type: BOOL
- label: "Kubernetes product parameters"
  name: "kubernetes"
  requires:
    - platform: "kubernetes_enabled"
  fields:
  - initial: cmp01
    name: kubernetes_compute_node01_hostname
    type: TEXT
  - initial: 192.168.0.0
    name: calico_network
    type: IP
  - initial: docker-prod-virtual.docker.mirantis.net/mirantis/kubernetes/hyperkube-amd64:v1.4.6-6
    name: hyperkube_image
    type: TEXT
  - initial: {{ deploy_network_subnet | subnet(102) }}
    name: kubernetes_compute_node02_deploy_address
    type: IP
  - initial: 'true'
    name: calico_enable_nat
    type: BOOL
  - initial: 172.16.10.107
    name: kubernetes_control_node01_address
    type: IP
  - initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/ctl:latest
    name: calicoctl_image
    type: TEXT
  - initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/node:latest
    name: calico_image
    type: TEXT
  - initial: 10.167.2.101
    name: kubernetes_compute_node01_single_address
    type: IP
  - initial: {{ control_network_subnet | subnet(10) }}
    name: kubernetes_control_address
    type: IP
  - initial: {{ deploy_network_subnet | subnet(13) }}
    name: kubernetes_control_node03_deploy_address
    type: IP
  - initial: 'true'
    name: etcd_ssl
    type: BOOL
  - initial: {{ deploy_network_subnet | subnet(11) }}
    name: kubernetes_control_node01_deploy_address
    type: IP
  - initial: ens4
    name: kubernetes_keepalived_vip_interface
    type: TEXT
  - initial: 172.17.10.106
    name: kubernetes_compute_node02_address
    type: IP
  - initial: ctl02
    name: kubernetes_control_node02_hostname
    type: TEXT
  - initial: 172.17.10.105
    name: kubernetes_compute_node01_address
    type: IP
  - initial: 172.16.10.109
    name: kubernetes_control_node03_address
    type: IP
  - initial: ctl01
    name: kubernetes_control_node01_hostname
    type: TEXT
  - initial: 172.16.10.108
    name: kubernetes_control_node02_address
    type: IP
  - initial: ctl03
    name: kubernetes_control_node03_hostname
    type: TEXT
  - initial: 10.167.2.102
    name: kubernetes_compute_node02_single_address
    type: IP
  - initial: {{ deploy_network_subnet | subnet(12) }}
    name: kubernetes_control_node02_deploy_address
    type: IP
  - initial: cmp02
    name: kubernetes_compute_node02_hostname
    type: TEXT
  - initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/cni:latest
    name: calico_cni_image
    type: TEXT
  - initial: {{ deploy_network_subnet | subnet(101) }}
    name: kubernetes_compute_node01_deploy_address
    type: IP
  - initial: '16'
    name: calico_netmask
    type: TEXT
- label: "OpenContrail service parameters"
  name: "opencontrail"
  requires:
    - opencontrail_enabled: True
  fields:
  - initial: ntw02
    name: opencontrail_control_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(101) }}
    name: opencontrail_router02_address
    type: IP
  - initial: {{ control_network_subnet | subnet(100) }}
    name: opencontrail_router01_address
    type: IP
  - initial: {{ tenant_network_subnet[-2:] }}
    name: opencontrail_compute_iface_mask
    type: TEXT
  - initial: nal01
    name: opencontrail_analytics_node01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(32) }}
    name: opencontrail_analytics_node02_address
    type: IP
  - initial: ntw01
    name: opencontrail_control_node01_hostname
    type: TEXT
  - initial: nal03
    name: opencontrail_analytics_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(30) }}
    name: opencontrail_analytics_address
    type: IP
  - initial: nal02
    name: opencontrail_analytics_node02_hostname
    type: TEXT
  - initial: nal
    name: opencontrail_analytics_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(23) }}
    name: opencontrail_control_node03_address
    type: IP
  - initial: ntw03
    name: opencontrail_control_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(33) }}
    name: opencontrail_analytics_node03_address
    type: IP
  - initial: rtr01
    name: opencontrail_router01_hostname
    type: TEXT
  - initial: ntw
    name: opencontrail_control_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(31) }}
    name: opencontrail_analytics_node01_address
    type: IP
  - initial: {{ control_network_subnet | subnet(22) }}
    name: opencontrail_control_node02_address
    type: IP
  - initial: rtr02
    name: opencontrail_router02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(21) }}
    name: opencontrail_control_node01_address
    type: IP
  - initial: bond0.${_param:tenant_vlan}
    name: opencontrail_compute_iface
    type: TEXT
    hidden: True
  - initial: {{ control_network_subnet | subnet(20) }}
    name: opencontrail_control_address
    type: IP
- label: "OpenStack product parameters"
  name: "openstack"
  requires:
    - platform: "openstack_enabled"
  fields:
  - initial: mdb02
    name: openstack_telemetry_node02_hostname
    type: TEXT
  - initial: {{ tenant_network_subnet | subnet(6) }}
    name: openstack_gateway_node01_tenant_address
    type: IP
  - initial: 10.167.6
    name: openstack_compute_rack01_tenant_subnet
    type: IP
  - initial: {{ control_network_subnet | subnet(80) }}
    name: openstack_proxy_address
    type: IP
  - initial: {{ control_network_subnet | subnet(226) }}
    name: openstack_gateway_node03_address
    type: IP
  - initial: {{ control_network_subnet | subnet(42) }}
    name: openstack_message_queue_node02_address
    type: IP
  - initial: prx
    name: openstack_proxy_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(81) }}
    name: openstack_proxy_node01_address
    type: IP
  - initial: msg03
    name: openstack_message_queue_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(76) }}
    name: openstack_telemetry_node01_address
    type: IP
  - initial: dbs02
    name: openstack_database_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(53) }}
    name: openstack_database_node03_address
    type: IP
  - initial: gtw01
    name: openstack_gateway_node01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(41) }}
    name: openstack_message_queue_node01_address
    type: IP
  - initial: physnet1
    name: openstack_nfv_sriov_network
    type: TEXT
    requires:
      - openstack_nfv_sriov_enabled: True
  - initial: {{ tenant_network_subnet | subnet(8) }}
    name: openstack_gateway_node03_tenant_address
    type: IP
  - initial: {{ control_network_subnet | subnet(43) }}
    name: openstack_message_queue_node03_address
    type: IP
  - initial: {{ control_network_subnet | subnet(51) }}
    name: openstack_database_node01_address
    type: IP
  - initial: {{ control_network_subnet | subnet(10) }}
    name: openstack_control_address
    type: IP
  - initial: msg01
    name: openstack_message_queue_node01_hostname
    type: TEXT
  - initial: gtw02
    name: openstack_gateway_node02_hostname
    type: TEXT
  - initial: ctl01
    name: openstack_control_node01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(77) }}
    name: openstack_telemetry_node02_address
    type: IP
  - initial: cmp
    name: openstack_compute_rack01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(225) }}
    name: openstack_gateway_node02_address
    type: IP
  - initial: 10.167.4
    name: openstack_compute_rack01_sigle_subnet
    type: IP
  - initial: {{ control_network_subnet | subnet(52) }}
    name: openstack_database_node02_address
    type: IP
  - initial: {{ control_network_subnet | subnet(40) }}
    name: openstack_message_queue_address
    type: IP
  - initial: prx02
    name: openstack_proxy_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(78) }}
    name: openstack_telemetry_node03_address
    type: IP
  - initial: msg
    name: openstack_message_queue_hostname
    type: TEXT
  - initial: mdb01
    name: openstack_telemetry_node01_hostname
    type: TEXT
  - initial: dbs03
    name: openstack_database_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(13) }}
    name: openstack_control_node03_address
    type: IP
  - initial: dbs01
    name: openstack_database_node01_hostname
    type: TEXT
  - initial: eth1
    name: compute_primary_first_nic
    type: TEXT
  - initial: gtw03
    name: openstack_gateway_node03_hostname
    type: TEXT
  - initial: dbs
    name: openstack_database_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(11) }}
    name: openstack_control_node01_address
    type: IP
  - initial: mdb03
    name: openstack_telemetry_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(50) }}
    name: openstack_database_address
    type: IP
  - initial: prx01
    name: openstack_proxy_node01_hostname
    type: TEXT
  - initial: mitaka
    name: openstack_version
    type: TEXT
  - initial: ctl02
    name: openstack_control_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(82) }}
    name: openstack_proxy_node02_address
    type: IP
  - initial: {{ control_network_subnet | subnet(224) }}
    name: openstack_gateway_node01_address
    type: IP
  - initial: {{ control_network_subnet | subnet(75) }}
    name: openstack_telemetry_address
    type: IP
  - initial: vxlan
    name: openstack_ovs_encapsulation_type
    type: TEXT
  - initial: ctl03
    name: openstack_control_node03_hostname
    type: TEXT
  - initial: eth1
    name: gateway_primary_first_nic
    type: TEXT
  - initial: {{ tenant_network_subnet | subnet(7) }}
    name: openstack_gateway_node02_tenant_address
    type: IP
  - initial: msg02
    name: openstack_message_queue_node02_hostname
    type: TEXT
  - initial: '16'
    name: openstack_nova_compute_hugepages_count
    type: IP
  - initial: ctl
    name: openstack_control_hostname
    type: TEXT
  - initial: 1,2,3,4,5,7,8,9,10,11
    name: openstack_nova_cpu_pinning
    type: TEXT
  - initial: 'False'
    name: openstack_ovs_dvr_enabled
    type: BOOL
  - initial: eth2
    name: gateway_primary_second_nic
    type: TEXT
  - initial: eth7
    name: openstack_nfv_sriov_pf_nic
    type: TEXT
  - initial: mdb
    name: openstack_telemetry_hostname
    type: TEXT
  - initial: 2416:2420
    name: openstack_ovs_encapsulation_vlan_range
    type: TEXT
  - initial: eth2
    name: compute_primary_second_nic
    type: TEXT
  - initial: '7'
    name: openstack_nfv_sriov_numvfs
    type: IP
  - initial: {{ control_network_subnet | subnet(12) }}
    name: openstack_control_node02_address
    type: IP
- label: "StackLight product parameters"
  name: "stacklight"
  requires:
    - stacklight_enabled: True
  fields:
  - initial: {{ control_network_subnet | subnet(73) }}
    name: stacklight_monitor_node03_address
    type: IP
  - initial: {{ control_network_subnet | subnet(88) }}
    name: stacklight_telemetry_node03_address
    type: IP
  - initial: mtr01
    name: stacklight_telemetry_node01_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(85) }}
    name: stacklight_telemetry_address
    type: IP
  - initial: mon02
    name: stacklight_monitor_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(61) }}
    name: stacklight_log_node01_address
    type: IP
  - initial: mon01
    name: stacklight_monitor_node01_hostname
    type: TEXT
  - initial: log02
    name: stacklight_log_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(86) }}
    name: stacklight_telemetry_node01_address
    type: IP
  - initial: {{ control_network_subnet | subnet(70) }}
    name: stacklight_monitor_address
    type: IP
  - initial: {{ control_network_subnet | subnet(60) }}
    name: stacklight_log_address
    type: IP
  - initial: {{ control_network_subnet | subnet(63) }}
    name: stacklight_log_node03_address
    type: IP
  - initial: mtr02
    name: stacklight_telemetry_node02_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(72) }}
    name: stacklight_monitor_node02_address
    type: IP
  - initial: log
    name: stacklight_log_hostname
    type: TEXT
  - initial: log01
    name: stacklight_log_node01_hostname
    type: TEXT
  - initial: mon03
    name: stacklight_monitor_node03_hostname
    type: TEXT
  - initial: mtr
    name: stacklight_telemetry_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(71) }}
    name: stacklight_monitor_node01_address
    type: IP
  - initial: log03
    name: stacklight_log_node03_hostname
    type: TEXT
  - initial: mon
    name: stacklight_monitor_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(87) }}
    name: stacklight_telemetry_node02_address
    type: IP
  - initial: mtr03
    name: stacklight_telemetry_node03_hostname
    type: TEXT
  - initial: {{ control_network_subnet | subnet(62) }}
    name: stacklight_log_node02_address
    type: IP
'''

