

module "plc" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-srv_noportsec.git"
    name = "${var.team_name}_plc"
    metadata_groups = "companies, ${var.team_name}, plc, servers, field"
    metadata_company_info = jsonencode(var.team_info)
    cidr = local.field_cidr
    host_index = 205
    network_id = module.field.networks["field"].network_id
    subnet_id = module.field.networks["field"].subnet_id
    image = var.images.server
    flavor = var.flavors.server
}
