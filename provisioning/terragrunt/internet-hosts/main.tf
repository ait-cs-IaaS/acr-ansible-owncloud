module "global_mail" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "global_mail"
    metadata_groups = "internet, mailservers"
    cidr = var.internet_cidr
    host_index = 2890000 # 240.108.25.17
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    image = var.images.server
    flavor = var.flavors.server
    #userdata = file("${path.module}/scripts/firewall_init.yml") # default
}

module "internet_clients" {
    source        = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    count = 1
    name = "internet_client_${count.index + 1}"
    metadata_groups = "internet_clients, clients, vnc"
    cidr = var.internet_cidr
    host_index = 101 + count.index # 240.64.0.101 - 240.64.0.xxx
    network_id = var.internet_network_id
    subnet_id = var.internet_subnet_id
    image = var.images.client
    flavor = var.flavors.client
}

module "attackers" {
    source             = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    for_each           = var.attackers
    name               = "attacker_${index(keys(var.attackers), each.key) + 1}"
    metadata_groups = "internet, attacker"
    cidr = var.internet_cidr
    host_index = each.value
    network_id         = var.internet_network_id
    subnet_id          = var.internet_subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "attack_mates" {
    source             = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    for_each           = var.attack_mates
    name               = "attack_mate_${index(keys(var.attackers), each.key) + 1}"
    metadata_groups = "internet, attacker, attackmate"
    cidr = var.internet_cidr
    host_index = each.value
    network_id         = var.internet_network_id
    subnet_id          = var.internet_subnet_id
    image = var.images.server
    flavor = var.flavors.server
}