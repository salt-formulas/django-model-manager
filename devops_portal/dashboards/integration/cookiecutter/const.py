CTX = '''
{% set private_key, public_key = generate_ssh_keypair() %}
general_params_action:
  - name: "base"
    label: "Base"
    doc: |
      Base
      ====
  
      This section covers basic deployment parameters. Supported deployment type is currently Physical for OpenStack. Kubernetes works with both Physical and Heat.

    fields:
      - name: "cluster_name"
        type: "TEXT"
        help_text: "Name of the cluster, used as cluster/<cluster_name>/ in directory structure."
        initial: "deployment_name"
      - name: "cluster_domain"
        type: "TEXT"
        help_text: "Domain name part of FQDN of cluster in the cluster."
        initial: "deploy-name.local"
      - name: "public_host"
        type: "TEXT"
        help_text: "Name or IP of public endpoint of the deployment."
        initial: "${_param:openstack_proxy_address}"
      - name: "reclass_repository"
        type: "TEXT"
        help_text: "URL from which salt master will fetch reclass metadata repository."
        initial: "https://github.com/Mirantis/mk-lab-salt-model.git"
      - name: "cookiecutter_template_url"
        type: "TEXT"
        initial: "git@github.com:Mirantis/mk2x-cookiecutter-reclass-model.git"
      - name: "cookiecutter_template_branch"
        type: "TEXT"
        initial: "master"
      - name: "deployment_type"
        type: "CHOICE"
        initial: "physical"
        choices:
          - - "heat"
            - "Heat"
          - - "physical"
            - "Physical"
      - name: "publication_method"
        type: "CHOICE"
        initial: "email"
        choices:
          - - "email"
            - "Send to e-mail address"
          - - "commit"
            - "Commit to repository"
  
  - name: "services"
    label: "Services"
    doc: |
      Services
      ========
  
      Here you can choose for which platform you want to generate the model. You can choose eighter OpenStack or Kubernetes. OpenContrail enabled parameter is for network engine of chosen platform. Right now supported only with OpenStack. If not enabled, OpenStack will have ovs as network engine. Kubernetes goes with Calico. Both platforms can go with CI/CD and StackLight.
    fields:
      - name: "platform"
        type: "CHOICE"
        help_text: "Enable either OpenStack or Kubernetes product sub-cluster"
        choices:
          - - "openstack_enabled"
            - "OpenStack"
          - - "kubernetes_enabled"
            - "Kubernetes"
        initial: "openstack_enabled"
      - name: "opencontrail_enabled"
        type: "BOOL"
        help_text: "Enable OpenContrail sub-cluster"
        initial: True
        label: "OpenContrail enabled"
      - name: "stacklight_enabled"
        type: "BOOL"
        help_text: "Enable StackLight sub-cluster"
        initial: True
        label: "StackLight enabled"
      - name: "cicd_enabled"
        type: "BOOL"
        help_text: "Enable CI/CD sub-cluster"
        initial: True
        label: "CI/CD enabled"
  - name: "networking"
    label: "Networking"
    doc: |
      Networking
      ==========
  
      This section covers basic Networking setup. Cookiecutter handles generic setup that includes dedicated management interface and two interfaces for workload. These two interfaces are in bond and have tagged subinterfaces for Control plane (Control network/VLAN) and Data plane (Tenant network/VLAN) traffic. Setup for NFV scenarios is not covered and needs to be done manually.

      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20network.png?raw=true
        :scale: 100 %
        :alt: Network diagram

    fields:
      - name: "dns_server01"
        type: "IP"
        help_text: "IP address of dns01 server"
        initial: "8.8.8.8"
        label: "DNS Server 01"
      - name: "dns_server02"
        type: "IP"
        help_text: "IP address of dns02 server"
        initial: "8.8.4.4"
        label: "DNS Server 02"
      - name: "deploy_network_subnet"
        type: IP
        help_text: "IP address of deploy network with network mask"
        initial: "10.0.0.0/24"
        mask: True
      - name: "deploy_network_gateway"
        type: IP
        help_text: "IP gateway address of deploy network"
        initial: "10.0.0.1"
      - name: "control_network_subnet"
        type: IP
        help_text: "IP address of control network with network mask"
        initial: "10.0.1.0/24"
        mask: True
      - name: "tenant_network_subnet"
        type: IP
        help_text: "IP address of tenant network with network mask"
        initial: "10.0.2.0/24"
        mask: True
      - name: "tenant_network_gateway"
        type: IP
        help_text: "IP gateway address of tenant network"
        initial: "10.0.2.1"
      - name: "control_vlan"
        type: TEXT
        help_text: "Contrail plane vlan ID"
        initial: "10"
        label: "Control VLAN"
      - name: "tenant_vlan"
        type: TEXT
        help_text: "Data plane vlan ID"
        initial: "20"
        label: "Tenant VLAN"
infra_params_action:
  - name: "salt"
    label: "Salt Master"
    fields:
      - name: "salt_master_address"
        type: "IP"
        help_text: "IP address of salt master on control network"
        initial: "{{ control_network_subnet | subnet(90) }}"
      - name: "salt_master_management_address"
        type: "IP"
        help_text: "IP address of salt master on management network"
        initial: "{{ deploy_network_subnet | subnet(90) }}"
      - name: "salt_master_hostname"
        type: "TEXT"
        help_text: "hostname of salt master"
        initial: "cfg01"
      - initial: "{{ 32|generate_password }}"
        name: salt_api_password
        type: TEXT
        hidden: True
  - name: "publication"
    label: "Publication Options"
    fields:
      - name: "email_address"
        type: "TEXT"
        help_text: "Generated reclass model will be sent to this address."
        requires: 
          - publication_method: "email"
      - name: "reclass_model_url"
        type: "TEXT"
        initial: {{ reclass_repository }}
        help_text: "Generated reclass model will be commited to this repo."
        requires: 
          - publication_method: "commit"
      - name: "reclass_model_branch"
        type: "TEXT"
        initial: "master"
        help_text: "Generated reclass model will be commited to this branch."
        requires: 
          - publication_method: "commit"
      - name: "reclass_model_credentials"
        type: "TEXT"
        initial: github-credentials
        help_text: "These credentials will be used to commit generated reclass."
        requires: 
          - publication_method: "commit"
  - name: "openstack_networking"
    label: "OpenStack Networking"
    doc: |
      OpenStack Networking
      ====================
      NFV feature generation is experimental. nfv req enabled parameter is for enabling hugepages and cpu pinning without dpdk. 
    requires:
      - platform: "openstack_enabled"
    fields:
      - name: "openstack_network_engine"
        help_text: "enables opencontrail sub-cluster if 'opencontrail'. Possible option is ovs and opencontrail"
        type: "TEXT"
        initial: "opencontrail"
        readonly: True
        requires:
          - opencontrail_enabled: True
      - name: "openstack_network_engine"
        help_text: "Possible options are ovs and opencontrail, this parameter is set automatically."
        type: "TEXT"
        initial: "ovs"
        readonly: True
        requires:
          - opencontrail_enabled: False
      - initial: vxlan
        name: openstack_ovs_encapsulation_type
        help_text: "Encapsulation type is either vlan or vxlan."
        type: TEXT
        requires:
          - opencontrail_enabled: False
      - initial: False
        name: openstack_nfv_sriov_enabled
        label: "OpenStack NFV SRIOV enabled"
        help_text: "enable SRIOV"
        type: BOOL
      - initial: False
        name: openstack_nfv_dpdk_enabled
        label: "OpenStack NFV DPDK enabled"
        help_text: "enable DPDK"
        type: BOOL
      - initial: False
        name: openstack_nova_compute_nfv_req_enabled
        label: "OpenStack Nova compute NFV req enabled"
        help_text: "enable cpu pinning and hugepages without dpdk"
        type: BOOL
product_params_action:
  - fields:
    - help_text: IP mask of control network
      hidden: true
      initial: '{{ control_network_subnet | netmask }}'
      name: control_network_netmask
      type: IP
    - help_text: IP mask of deploy network
      hidden: true
      initial: '{{ deploy_network_subnet | netmask }}'
      name: deploy_network_netmask
      type: IP
    - help_text: NIC that is used for pxe of KVM servers
      initial: eth0
      name: infra_deploy_nic
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: IP address of a KVM node01 on control network
      initial: '{{ control_network_subnet | subnet(241) }}'
      name: infra_kvm01_control_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: IP address of a KVM node01 on management network
      initial: '{{ deploy_network_subnet | subnet(241) }}'
      name: infra_kvm01_deploy_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: hostname of a KVM node01
      initial: kvm01
      name: infra_kvm01_hostname
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: IP address of a KVM node02 on control network
      initial: '{{ control_network_subnet | subnet(242) }}'
      name: infra_kvm02_control_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: IP address of KVM node02 on management network
      initial: '{{ deploy_network_subnet | subnet(242) }}'
      name: infra_kvm02_deploy_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: hostname of a KVM node02
      initial: kvm02
      name: infra_kvm02_hostname
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: IP address of a KVM node03 on control network
      initial: '{{ control_network_subnet | subnet(243) }}'
      name: infra_kvm03_control_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: IP address of KVM node03 on management network
      initial: '{{ deploy_network_subnet | subnet(243) }}'
      name: infra_kvm03_deploy_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: hostname of a KVM node03
      initial: kvm03
      name: infra_kvm03_hostname
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: IP VIP address of KVM cluster
      initial: '{{ control_network_subnet | subnet(240) }}'
      name: infra_kvm_vip_address
      requires:
      - deployment_type: physical
      type: IP
    - help_text: First NIC in KVM bond
      initial: eth1
      name: infra_primary_first_nic
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: Second NIC in KVM bond
      initial: eth2
      name: infra_primary_second_nic
      requires:
      - deployment_type: physical
      type: TEXT
    - help_text: number of compute nodes to be generated
      initial: '100'
      name: openstack_compute_count
      requires:
      - platform: openstack_enabled
      type: TEXT
    - help_text: Hash of salt_api_passfor
      hidden: true
      initial: '{{ salt_api_password|hash_password }}'
      name: salt_api_password_hash
      type: TEXT
    - help_text: IP mask of tenant network
      hidden: true
      initial: '{{ tenant_network_subnet | netmask }}'
      name: tenant_network_netmask
      type: IP
    label: Infrastructure product parameters
    name: infra
    doc: |
      Infrastructure product parameters
      =================================
  
      This section covers KVM nodes which hosts Control plane VMs. By default cookicutter uses three KVM nodes. These nodes can host OpenStack Control plane, CI/CD, StackLight or OpenContrail VMs based on previous selection.

      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20kvm.png?raw=true
        :scale: 100 %
        :alt: KVM diagram

  - fields:
    - help_text: IP address of cicd control node01
      initial: '{{ control_network_subnet | subnet(91) }}'
      name: cicd_control_node01_address
      type: IP
    - help_text: hostname of cicd control node01
      initial: cid01
      name: cicd_control_node01_hostname
      type: TEXT
    - help_text: IP address of cicd control node02
      initial: '{{ control_network_subnet | subnet(92) }}'
      name: cicd_control_node02_address
      type: IP
    - help_text: hostname of cicd control node02
      hidden: true
      initial: cid02
      name: cicd_control_node02_hostname
      type: TEXT
    - help_text: IP address of cicd control node03
      initial: '{{ control_network_subnet | subnet(93) }}'
      name: cicd_control_node03_address
      type: IP
    - help_text: hostname of cicd control node03
      initial: cid03
      name: cicd_control_node03_hostname
      type: TEXT
    - help_text: IP VIP address of cicd control cluster
      initial: '{{ control_network_subnet | subnet(90) }}'
      name: cicd_control_vip_address
      type: IP
    - help_text: hostname of cicd control cluster
      initial: cid
      name: cicd_control_vip_hostname
      type: TEXT
    - help_text: Private key for Jenkins. It is generated automatically.
      hidden: true
      initial: |-
        {{ private_key|indent(8) }}
      name: cicd_private_key
      type: LONG_TEXT
    - help_text: Public key for Jenkins. It is generated automatically.
      hidden: true
      initial: '{{ public_key }}'
      name: cicd_public_key
      type: LONG_TEXT
    - help_text: enable openldap authentication
      initial: true
      name: openldap_enabled
      type: BOOL
    - initial: "${_param:cluster_name}"
      name: openldap_organisation
      type: TEXT
    - initial: "dc=${_param:cluster_name},dc=local"
      name: openldap_dn
      type: TEXT
    - initial: "${_param:cluster_public_host}"
      name: openldap_domain
      type: TEXT
    label: CI/CD product parameters
    name: cicd
    doc: |
      CI/CD product parameters
      =================================
  
      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20cicd.png?raw=true
        :scale: 100 %
        :alt: StackLight control diagram

    requires:
    - cicd_enabled: true
  - fields:
    - help_text: Image with CNI binaries
      initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/cni:latest
      name: calico_cni_image
      type: TEXT
    - help_text: ''
      initial: 'true'
      name: calico_enable_nat
      type: BOOL
    - help_text: Image with Calico
      initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/node:latest
      name: calico_image
      type: TEXT
    - help_text: Netmask of calico_network
      initial: '16'
      name: calico_netmask
      type: TEXT
    - help_text: Network that is used for kubernetes containers
      initial: 192.168.0.0
      name: calico_network
      type: IP
    - help_text: Image with Calicoctl command
      initial: docker-prod-virtual.docker.mirantis.net/mirantis/projectcalico/calico/ctl:latest
      name: calicoctl_image
      type: TEXT
    - help_text: enable ssl for etcd
      initial: 'true'
      name: etcd_ssl
      type: BOOL
    - help_text: Image with Kubernetes.
      initial: docker-prod-virtual.docker.mirantis.net/mirantis/kubernetes/hyperkube-amd64:v1.4.6-6
      name: hyperkube_image
      type: TEXT
    - help_text: IP address of kubernetes compute node01
      initial: 172.17.10.105
      name: kubernetes_compute_node01_address
      type: IP
    - help_text: ''
      initial: '{{ deploy_network_subnet | subnet(101) }}'
      name: kubernetes_compute_node01_deploy_address
      type: IP
    - help_text: hostname of kubernetes compute node01
      initial: cmp01
      name: kubernetes_compute_node01_hostname
      type: TEXT
    - help_text: ''
      initial: 10.167.2.101
      name: kubernetes_compute_node01_single_address
      type: IP
    - help_text: IP address of kubernetes compute node02
      initial: 172.17.10.106
      name: kubernetes_compute_node02_address
      type: IP
    - help_text: ''
      initial: '{{ deploy_network_subnet | subnet(102) }}'
      name: kubernetes_compute_node02_deploy_address
      type: IP
    - help_text: hostname of kubernetes compute node02
      initial: cmp02
      name: kubernetes_compute_node02_hostname
      type: TEXT
    - help_text: ''
      initial: 10.167.2.102
      name: kubernetes_compute_node02_single_address
      type: IP
    - help_text: enable cpu pinning and hugepages without dpdk
      initial: '{{ control_network_subnet | subnet(10) }}'
      name: kubernetes_control_address
      type: IP
    - help_text: IP address of kubernetes control node01
      initial: 172.16.10.107
      name: kubernetes_control_node01_address
      type: IP
    - help_text: ''
      initial: '{{ deploy_network_subnet | subnet(11) }}'
      name: kubernetes_control_node01_deploy_address
      type: IP
    - help_text: hostname of kubernetes control node01
      initial: ctl01
      name: kubernetes_control_node01_hostname
      type: TEXT
    - help_text: IP address of kubernetes control node02
      initial: 172.16.10.108
      name: kubernetes_control_node02_address
      type: IP
    - help_text: ''
      initial: '{{ deploy_network_subnet | subnet(12) }}'
      name: kubernetes_control_node02_deploy_address
      type: IP
    - help_text: hostname of kubernetes control node02
      initial: ctl02
      name: kubernetes_control_node02_hostname
      type: TEXT
    - help_text: IP address of kubernetes control node03
      initial: 172.16.10.109
      name: kubernetes_control_node03_address
      type: IP
    - help_text: ''
      initial: '{{ deploy_network_subnet | subnet(13) }}'
      name: kubernetes_control_node03_deploy_address
      type: IP
    - help_text: hostname of kubernetes control node03
      initial: ctl03
      name: kubernetes_control_node03_hostname
      type: TEXT
    - help_text: Interface used for keepalived VIP
      initial: ens4
      name: kubernetes_keepalived_vip_interface
      type: TEXT
    label: Kubernetes product parameters
    name: kubernetes
    requires:
    - platform: kubernetes_enabled
  - fields:
    - help_text: ''
      initial: '{{ control_network_subnet | subnet(30) }}'
      name: opencontrail_analytics_address
      type: IP
    - help_text: ''
      initial: nal
      name: opencontrail_analytics_hostname
      type: TEXT
    - help_text: IP address of a opencontrail analytics node01 on control network
      initial: '{{ control_network_subnet | subnet(31) }}'
      name: opencontrail_analytics_node01_address
      type: IP
    - help_text: hostname of a opencontrail analytics node01 on control network
      initial: nal01
      name: opencontrail_analytics_node01_hostname
      type: TEXT
    - help_text: IP address of a opencontrail analytics node02 on control network
      initial: '{{ control_network_subnet | subnet(32) }}'
      name: opencontrail_analytics_node02_address
      type: IP
    - help_text: hostname of a opencontrail analytics node02 on control network
      initial: nal02
      name: opencontrail_analytics_node02_hostname
      type: TEXT
    - help_text: IP address of a opencontrail analytics node03 on control network
      initial: '{{ control_network_subnet | subnet(33) }}'
      name: opencontrail_analytics_node03_address
      type: IP
    - help_text: hostname of a opencontrail analytics node03 on control network
      initial: nal03
      name: opencontrail_analytics_node03_hostname
      type: TEXT
    - help_text: mask that is used in opencontrail. Automatically taken from tenant
        network.
      hidden: true
      initial: '{{ tenant_network_subnet[-2:] }}'
      name: opencontrail_compute_iface_mask
      type: TEXT
    - help_text: IP VIP address of opencontrail control cluster
      initial: '{{ control_network_subnet | subnet(20) }}'
      name: opencontrail_control_address
      type: IP
    - help_text: hostname of opencontrail control cluster
      initial: ntw
      name: opencontrail_control_hostname
      type: TEXT
    - help_text: IP address of a opencontrail control node01 on control network
      initial: '{{ control_network_subnet | subnet(21) }}'
      name: opencontrail_control_node01_address
      type: IP
    - help_text: hostname of a opencontrail control node01 on control network
      initial: ntw01
      name: opencontrail_control_node01_hostname
      type: TEXT
    - help_text: IP address of a opencontrail control node02 on control network
      initial: '{{ control_network_subnet | subnet(22) }}'
      name: opencontrail_control_node02_address
      type: IP
    - help_text: hostname of a opencontrail control node02 on control network
      initial: ntw02
      name: opencontrail_control_node02_hostname
      type: TEXT
    - help_text: IP address of a opencontrail control node03 on control network
      initial: '{{ control_network_subnet | subnet(23) }}'
      name: opencontrail_control_node03_address
      type: IP
    - help_text: hostname of a opencontrail control node03 on control network
      initial: ntw03
      name: opencontrail_control_node03_hostname
      type: TEXT
    - help_text: IP address of opencontrail gateway 01 router for BGP
      initial: '{{ control_network_subnet | subnet(100) }}'
      name: opencontrail_router01_address
      type: IP
    - help_text: hostname of opencontrail gateway 01 router
      initial: rtr01
      name: opencontrail_router01_hostname
      type: TEXT
    - help_text: IP address of opencontrail gateway 02 router for BGP
      initial: '{{ control_network_subnet | subnet(101) }}'
      name: opencontrail_router02_address
      type: IP
    - help_text: hostname of opencontrail gateway 02 router
      initial: rtr02
      name: opencontrail_router02_hostname
      type: TEXT
    label: OpenContrail service parameters
    name: opencontrail
    doc: |
      OpenContrail service parameters
      =================================
  
      OpenContrail Control plane runs on six VMs in total - three for Control and three for Analytics.

      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20opencontrail.png?raw=true
        :scale: 100 %
        :alt: OpenContrail control diagram

      OpenContrail kernel vRouter setup by cookiecutter:

      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20compute.png?raw=true
        :scale: 100 %
        :alt: compute diagram

    requires:
    - opencontrail_enabled: true
  - fields:
    - help_text: First NIC in OpenStack compute bond
      initial: eth1
      name: compute_primary_first_nic
      type: TEXT
    - help_text: Second NIC in OpenStack compute bond
      initial: eth2
      name: compute_primary_second_nic
      type: TEXT
    - help_text: First NIC in OVS gateway bond
      initial: eth1
      name: gateway_primary_first_nic
      type: TEXT
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: Second NIC in OVS gateway bond
      initial: eth2
      name: gateway_primary_second_nic
      type: TEXT
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: compute hostname prefix
      initial: cmp
      name: openstack_compute_rack01_hostname
      type: TEXT
    - help_text: control plane network prefix for compute nodes
      initial: '{{ ".".join(control_network_subnet.split(".")[:3]) }}'
      name: openstack_compute_rack01_sigle_subnet
      type: IP
    - help_text: data plane network prefix for compute nodes
      initial: '{{ ".".join(tenant_network_subnet.split(".")[:3]) }}'
      name: openstack_compute_rack01_tenant_subnet
      type: TEXT
    - help_text: IP VIP address of control cluster on control network
      initial: '{{ control_network_subnet | subnet(10) }}'
      name: openstack_control_address
      type: IP
    - help_text: hostname of VIP control cluster
      initial: ctl
      name: openstack_control_hostname
      type: TEXT
    - help_text: IP address of a control node01 on control network
      initial: '{{ control_network_subnet | subnet(11) }}'
      name: openstack_control_node01_address
      type: IP
    - help_text: hostname of a control node01
      initial: ctl01
      name: openstack_control_node01_hostname
      type: TEXT
    - help_text: IP address of a control node02 on control network
      initial: '{{ control_network_subnet | subnet(12) }}'
      name: openstack_control_node02_address
      type: IP
    - help_text: hostname of a control node02
      initial: ctl02
      name: openstack_control_node02_hostname
      type: TEXT
    - help_text: IP address of a control node03 on control network
      initial: '{{ control_network_subnet | subnet(13) }}'
      name: openstack_control_node03_address
      type: IP
    - help_text: hostname of a control node03
      initial: ctl03
      name: openstack_control_node03_hostname
      type: TEXT
    - help_text: IP VIP address of database cluster on control network
      initial: '{{ control_network_subnet | subnet(50) }}'
      name: openstack_database_address
      type: IP
    - help_text: hostname of VIP database cluster
      initial: dbs
      name: openstack_database_hostname
      type: TEXT
    - help_text: IP address of a database node01 on control network
      initial: '{{ control_network_subnet | subnet(51) }}'
      name: openstack_database_node01_address
      type: IP
    - help_text: hostname of a database node01
      initial: dbs01
      name: openstack_database_node01_hostname
      type: TEXT
    - help_text: IP address of a database node02 on control network
      initial: '{{ control_network_subnet | subnet(52) }}'
      name: openstack_database_node02_address
      type: IP
    - help_text: hostname of a database node02
      initial: dbs02
      name: openstack_database_node02_hostname
      type: TEXT
    - help_text: IP address of a database node03 on control network
      initial: '{{ control_network_subnet | subnet(53) }}'
      name: openstack_database_node03_address
      type: IP
    - help_text: hostname of a database node03
      initial: dbs03
      name: openstack_database_node03_hostname
      type: TEXT
    - help_text: IP address of gateway node01
      initial: '{{ control_network_subnet | subnet(224) }}'
      name: openstack_gateway_node01_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: hostname of gateway node01
      initial: gtw01
      name: openstack_gateway_node01_hostname
      type: TEXT
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP tenant address of gateway node01
      initial: '{{ tenant_network_subnet | subnet(6) }}'
      name: openstack_gateway_node01_tenant_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP address of gateway node02
      initial: '{{ control_network_subnet | subnet(225) }}'
      name: openstack_gateway_node02_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: hostname of gateway node02
      initial: gtw02
      name: openstack_gateway_node02_hostname
      type: TEXT
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP tenant address of gateway node02
      initial: '{{ tenant_network_subnet | subnet(7) }}'
      name: openstack_gateway_node02_tenant_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP address of gateway node03
      initial: '{{ control_network_subnet | subnet(226) }}'
      name: openstack_gateway_node03_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: hostname of gateway node03
      initial: gtw03
      name: openstack_gateway_node03_hostname
      type: TEXT
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP tenant address of gateway node03
      initial: '{{ tenant_network_subnet | subnet(8) }}'
      name: openstack_gateway_node03_tenant_address
      type: IP
      requires:
        - openstack_network_engine: 'ovs'
    - help_text: IP VIP address of message queue cluster on control network
      initial: '{{ control_network_subnet | subnet(40) }}'
      name: openstack_message_queue_address
      type: IP
    - help_text: hostname of VIP message queue cluster
      initial: msg
      name: openstack_message_queue_hostname
      type: TEXT
    - help_text: IP address of a message queue node01 on control network
      initial: '{{ control_network_subnet | subnet(41) }}'
      name: openstack_message_queue_node01_address
      type: IP
    - help_text: hostname of a message queue node01
      initial: msg01
      name: openstack_message_queue_node01_hostname
      type: TEXT
    - help_text: IP address of a message queue node02 on control network
      initial: '{{ control_network_subnet | subnet(42) }}'
      name: openstack_message_queue_node02_address
      type: IP
    - help_text: hostname of a message queue node02
      initial: msg02
      name: openstack_message_queue_node02_hostname
      type: TEXT
    - help_text: IP address of a message queue node03 on control network
      initial: '{{ control_network_subnet | subnet(43) }}'
      name: openstack_message_queue_node03_address
      type: IP
    - help_text: hostname of a message queue node03
      initial: msg03
      name: openstack_message_queue_node03_hostname
      type: TEXT
    - help_text: Tag of the physical network the sriov interface belongs to
      initial: physnet1
      name: openstack_nfv_sriov_network
      requires:
      - openstack_nfv_sriov_enabled: true
      type: TEXT
    - help_text: number of allocated Virtual Function interfaces
      initial: '7'
      name: openstack_nfv_sriov_numvfs
      requires:
      - openstack_nfv_sriov_enabled: true
      type: TEXT
    - help_text: Physical Function interface providing the Virtual Functions
      initial: eth7
      name: openstack_nfv_sriov_pf_nic
      requires:
      - openstack_nfv_sriov_enabled: true
      type: TEXT
    - help_text: number of Hugepages if dpdk enabled
      initial: '16'
      name: openstack_nova_compute_hugepages_count
      requires_or:
      - openstack_nfv_dpdk_enabled: true
      - openstack_nova_compute_nfv_req_enabled: true
      type: TEXT
    - help_text: pinned cpu's for nova
      initial: 1,2,3,4,5,7,8,9,10,11
      name: openstack_nova_cpu_pinning
      requires_or:
      - openstack_nfv_dpdk_enabled: true
      - openstack_nova_compute_nfv_req_enabled: true
      type: TEXT
    - help_text: If openstack_network_engine == ovs. Enables dvr.
      initial: false
      name: openstack_ovs_dvr_enabled
      requires:
      - openstack_network_engine: ovs
      type: BOOL
    - help_text: vlan range for OVS networks, valid for vlan encapslulation_type
      initial: 2416:2420
      name: openstack_ovs_encapsulation_vlan_range
      requires:
      - openstack_network_engine: ovs
      - openstack_ovs_encapsulation_type: vlan
      type: TEXT
    - help_text: IP VIP address of proxy cluster on control network
      initial: '{{ control_network_subnet | subnet(80) }}'
      name: openstack_proxy_address
      type: IP
    - help_text: hostname of VIP proxy cluster
      initial: prx
      name: openstack_proxy_hostname
      type: TEXT
    - help_text: IP address of a proxy node01 on control network
      initial: '{{ control_network_subnet | subnet(81) }}'
      name: openstack_proxy_node01_address
      type: IP
    - help_text: hostname of a proxy node01
      initial: prx01
      name: openstack_proxy_node01_hostname
      type: TEXT
    - help_text: IP address of a proxy node02 on control network
      initial: '{{ control_network_subnet | subnet(82) }}'
      name: openstack_proxy_node02_address
      type: IP
    - help_text: hostname of a proxy node02
      initial: prx02
      name: openstack_proxy_node02_hostname
      type: TEXT
    - help_text: IP VIP address of telemetry cluster on control network
      initial: '{{ control_network_subnet | subnet(75) }}'
      name: openstack_telemetry_address
      type: IP
    - help_text: hostname of VIP telemetry cluster
      initial: mdb
      name: openstack_telemetry_hostname
      type: TEXT
    - help_text: IP address of a telemetry node01 on control network
      initial: '{{ control_network_subnet | subnet(76) }}'
      name: openstack_telemetry_node01_address
      type: IP
    - help_text: hostname of a telemetry node01
      initial: mdb01
      name: openstack_telemetry_node01_hostname
      type: TEXT
    - help_text: IP address of a telemetry node02 on control network
      initial: '{{ control_network_subnet | subnet(77) }}'
      name: openstack_telemetry_node02_address
      type: IP
    - help_text: hostname of a telemetry node02
      initial: mdb02
      name: openstack_telemetry_node02_hostname
      type: TEXT
    - help_text: IP address of a telemetry node03 on control network
      initial: '{{ control_network_subnet | subnet(78) }}'
      name: openstack_telemetry_node03_address
      type: IP
    - help_text: hostname of a telemetry node03
      initial: mdb03
      name: openstack_telemetry_node03_hostname
      type: TEXT
    - help_text: version of OpenStack
      initial: mitaka
      name: openstack_version
      type: TEXT
    label: OpenStack product parameters
    name: openstack
    doc: |
      OpenStack product parameters
      =================================
  
      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20openstack.png?raw=true
        :scale: 100 %
        :alt: OpenStack control diagram

    requires:
    - platform: openstack_enabled
  - fields:
    - help_text: IP VIP address of stacklight logging cluster
      initial: '{{ control_network_subnet | subnet(60) }}'
      name: stacklight_log_address
      type: IP
    - help_text: hostname of stacklight logging cluster
      initial: log
      name: stacklight_log_hostname
      type: TEXT
    - help_text: IP address of stacklight logging node01
      initial: '{{ control_network_subnet | subnet(61) }}'
      name: stacklight_log_node01_address
      type: IP
    - help_text: hostname of stacklight logging node01
      initial: log01
      name: stacklight_log_node01_hostname
      type: TEXT
    - help_text: IP address of stacklight logging node02
      initial: '{{ control_network_subnet | subnet(62) }}'
      name: stacklight_log_node02_address
      type: IP
    - help_text: hostname of stacklight logging node02
      initial: log02
      name: stacklight_log_node02_hostname
      type: TEXT
    - help_text: IP address of stacklight logging node03
      initial: '{{ control_network_subnet | subnet(63) }}'
      name: stacklight_log_node03_address
      type: IP
    - help_text: hostname of stacklight logging node03
      initial: log03
      name: stacklight_log_node03_hostname
      type: TEXT
    - help_text: IP VIP address of stacklight monitoring cluster
      initial: '{{ control_network_subnet | subnet(70) }}'
      name: stacklight_monitor_address
      type: IP
    - help_text: hostname of stacklight monitoring cluster
      initial: mon
      name: stacklight_monitor_hostname
      type: TEXT
    - help_text: IP address of stacklight monitoring node01
      initial: '{{ control_network_subnet | subnet(71) }}'
      name: stacklight_monitor_node01_address
      type: IP
    - help_text: hostname of stacklight monitoring node01
      initial: mon01
      name: stacklight_monitor_node01_hostname
      type: TEXT
    - help_text: IP address of stacklight monitoring node02
      initial: '{{ control_network_subnet | subnet(72) }}'
      name: stacklight_monitor_node02_address
      type: IP
    - help_text: hostname of stacklight monitoring node02
      initial: mon02
      name: stacklight_monitor_node02_hostname
      type: TEXT
    - help_text: IP address of stacklight monitoring node03
      initial: '{{ control_network_subnet | subnet(73) }}'
      name: stacklight_monitor_node03_address
      type: IP
    - help_text: hostname of stacklight monitoring node03
      initial: mon03
      name: stacklight_monitor_node03_hostname
      type: TEXT
    - help_text: IP VIP address of stacklight telemetry cluster
      initial: '{{ control_network_subnet | subnet(85) }}'
      name: stacklight_telemetry_address
      type: IP
    - help_text: hostname of stacklight telemetry cluster
      initial: mtr
      name: stacklight_telemetry_hostname
      type: TEXT
    - help_text: IP address of stacklight telemetry node01
      initial: '{{ control_network_subnet | subnet(86) }}'
      name: stacklight_telemetry_node01_address
      type: IP
    - help_text: hostname of stacklight telemetry node01
      initial: mtr01
      name: stacklight_telemetry_node01_hostname
      type: TEXT
    - help_text: IP address of stacklight telemetry node02
      initial: '{{ control_network_subnet | subnet(87) }}'
      name: stacklight_telemetry_node02_address
      type: IP
    - help_text: hostname of stacklight telemetry node02
      initial: mtr02
      name: stacklight_telemetry_node02_hostname
      type: TEXT
    - help_text: IP address of stacklight telemetry node03
      initial: '{{ control_network_subnet | subnet(88) }}'
      name: stacklight_telemetry_node03_address
      type: IP
    - help_text: hostname of stacklight telemetry node03
      initial: mtr03
      name: stacklight_telemetry_node03_hostname
      type: TEXT
    label: StackLight product parameters
    name: stacklight
    doc: |
      StackLight product parameters
      =================================
  
      .. figure:: https://github.com/mceloud/images/blob/master/cookiecutter%20-%20stacklight.png?raw=true
        :scale: 100 %
        :alt: StackLight control diagram

    requires:
    - stacklight_enabled: true
'''

