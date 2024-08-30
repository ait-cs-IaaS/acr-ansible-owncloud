

module "hmi" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_hmi"
    metadata_groups = "companies, ${var.team_name}, supervisory, hmi, servers, clients, vnc, facility"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.supervisory_cidr
    host_index = 178
    network_id = module.supervisory.networks["supervisory"].network_id
    subnet_id = module.supervisory.networks["supervisory"].subnet_id
    image = var.images.client
    flavor = var.flavors.client
}

# module "historian"{
#     source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
#     name = "${var.team_name}_historian"
#     metadata_groups = "companies, ${var.team_name}, supervisory, historian, servers"
#     metadata_company_info = jsonencode(var.team_info)
#     cidr = local.supervisory_cidr
#     host_index = 30
#     network_id = module.supervisory.networks["supervisory"].network_id
#     subnet_id = module.supervisory.networks["supervisory"].subnet_id
#     image = var.images.server
#     flavor = var.flavors.server
# }

# module "control_room"{
#     source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
#     name = "${var.team_name}_control_room"
#     metadata_groups = "companies, ${var.team_name}, supervisory, control_room, servers"
#     metadata_company_info = jsonencode(var.team_info)
#     cidr = local.supervisory_cidr
#     host_index = 52
#     network_id = module.supervisory.networks["supervisory"].network_id
#     subnet_id = module.supervisory.networks["supervisory"].subnet_id
#     image = var.images.server
#     flavor = var.flavors.server
# }

module "workstation"{
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_workstation"
    metadata_groups = "companies, ${var.team_name}, supervisory, clients_workstation, servers, clients, vnc"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.supervisory_cidr
    host_index = 45
    network_id = module.supervisory.networks["supervisory"].network_id
    subnet_id = module.supervisory.networks["supervisory"].subnet_id
    image = var.images.client
    flavor = var.flavors.client
}

module "lanturtle" {
  source             = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
  name           = "${var.team_name}_lanturtle"
  metadata_groups                = "companies, ${var.team_name}, supervisory, lanturtle"
  cidr = var.internet_cidr
  host_index = var.lanturtle_internet_host_index
  metadata_company_info = jsonencode(var.team_info)
  image = var.images.server
  flavor = var.flavors.server
  network_id         = var.internet_network_id
  subnet_id          = var.internet_subnet_id
  additional_networks = {
    supervisory = {
        name = module.supervisory.networks["supervisory"].name
        cidr = module.supervisory.networks["supervisory"].cidr
        host_index = 202
        network_id = module.supervisory.networks["supervisory"].network_id
        subnet_id = module.supervisory.networks["supervisory"].subnet_id
    }
  }
}