module "clients_csirt" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    count = 2
    name = "${var.team_name}_csirt_client_${count.index + 1}"
    metadata_groups = "${var.team_name}, companies, soc, clients_csirt, clients, vnc"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.soc_cidr
    host_index = 10 + count.index
    network_id = module.soc-access.networks["soc"].network_id
    subnet_id = module.soc-access.networks["soc"].subnet_id
    image = var.images.client
    flavor = var.flavors.client
}

module "elk" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_elk"
    metadata_groups = "${var.team_name}, companies, soc, elk, servers"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.soc_cidr
    host_index = 37
    network_id = module.soc-access.networks["soc"].network_id
    subnet_id = module.soc-access.networks["soc"].subnet_id
    image = var.images.elk
    flavor = var.flavors.elk
}