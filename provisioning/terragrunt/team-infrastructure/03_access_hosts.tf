module "clients_employees" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    count = 1
    name = "${var.team_name}_employee_${count.index + 1}"
    metadata_groups = "companies, ${var.team_name}, access, clients_employees, clients"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.access_cidr
    host_index = 50 + count.index
    network_id = module.soc-access.networks["access"].network_id
    subnet_id = module.soc-access.networks["access"].subnet_id
    image = var.images.client
    flavor = var.flavors.client
}

module "fileshare" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_fileshare"
    metadata_groups = "companies, ${var.team_name}, access, fileshare, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.access_cidr
    host_index = 178
    network_id = module.soc-access.networks["access"].network_id
    subnet_id = module.soc-access.networks["access"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}

module "clients_regular" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    count = 1
    name = "${var.team_name}_participant_client_${count.index + 1}"
    metadata_groups = "companies, ${var.team_name}, access, clients, clients_regular, vnc"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.access_cidr
    host_index = 10 + count.index
    network_id = module.soc-access.networks["access"].network_id
    subnet_id = module.soc-access.networks["access"].subnet_id
    image = var.images.client
    flavor = var.flavors.client
}