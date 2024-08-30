module "cloud" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    count = var.team_info.cloud ? 1 : 0
    name = "${var.team_name}_cloud"
    metadata_groups = "companies, ${var.team_name}, dmz, cloud, ${var.team_name}_proxied, proxied, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.dmz_cidr
    host_index = 9
    network_id = module.dmz.networks["dmz"].network_id
    subnet_id = module.dmz.networks["dmz"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "proxy" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_proxy"
    metadata_groups = "companies, ${var.team_name}, dmz, proxy, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.dmz_cidr
    host_index = 17
    network_id = module.dmz.networks["dmz"].network_id
    subnet_id = module.dmz.networks["dmz"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "webserver" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_webserver"
    metadata_groups = "companies, ${var.team_name}, dmz, webserver, ${var.team_name}_proxied, proxied, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.dmz_cidr
    host_index = 50
    network_id = module.dmz.networks["dmz"].network_id
    subnet_id = module.dmz.networks["dmz"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "mailserver_intern" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_mail"
    metadata_groups = "companies, ${var.team_name}, dmz, ${var.team_name}_proxied, proxied, mailserver_intern, mailservers, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.dmz_cidr
    host_index = 100
    network_id = module.dmz.networks["dmz"].network_id
    subnet_id = module.dmz.networks["dmz"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "application_server" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_application_server"
    metadata_groups = "companies, ${var.team_name}, dmz, application_server, ${var.team_name}_proxied, proxied, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.dmz_cidr
    host_index = 35
    network_id = module.dmz.networks["dmz"].network_id
    subnet_id = module.dmz.networks["dmz"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}