module "mgmthost" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "mgmthost"
    metadata_groups = "mgmthosts"
    image = var.images.server
    flavor = var.flavors.server
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    cidr = var.internet_cidr
    host_index = 42
    floating_ip = true
    fip_pool = var.fip_pool
    additional_networks = local.mgmt_networks
}

module "mailgin" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "mailgin"
    metadata_groups = "management"
    image = var.images.server
    flavor = var.flavors.server
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    cidr = var.internet_cidr
    host_index = 41
    floating_ip = true
    fip_pool = var.fip_pool
    additional_networks = local.mailgin_networks
}

module "learners" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "learners"
    metadata_groups = "management"
    image = var.images.server
    flavor = var.flavors.server
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    cidr = var.internet_cidr
    host_index = 99
    floating_ip = true
    fip_pool = var.fip_pool
    additional_networks = local.learners_networks
}

module "venjix" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "venjix"
    metadata_groups = "venjixi, management"
    image = var.images.server
    flavor = var.flavors.server
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    cidr = var.internet_cidr
    host_index = 230
    floating_ip = true
    fip_pool = var.fip_pool
    additional_networks = local.venjix_networks
}

module "control" {
  source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
  count                    = 1
  name                     = "control_client_${count.index + 1}"
  metadata_groups          = "control, clients, vnc"
  cidr                     = var.internet_cidr
  host_index               = 61 + count.index
  network_id               = var.internet_network_id
  subnet_id                = var.internet_subnet_id
  image                    = var.images.client
  flavor                   = var.flavors.client
  additional_networks      = local.control_networks
}