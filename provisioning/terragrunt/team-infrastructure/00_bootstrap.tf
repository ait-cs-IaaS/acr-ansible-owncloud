module "dmz" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-vmnets.git"

    # base network / parent network
    parent_network_id = var.internet_network_id #network ID from the fake-internet module
    parent_subnet_id = var.internet_subnet_id #subnet ID from the fake-internet module
    parent_cidr = var.internet_cidr
    parent_dns_nameservers = var.internet_dns_ip
    parent_gateway_ip = var.internet_gateway_ip

    #parent_network_dns = #IP of Internet DNS Server
    firewall_name = "${var.team_name}_firewall_external"
    firewall_image = var.images.server
    firewall_flavor = var.flavors.server
    firewall_host_index = var.internet_host_index #internet address
    metadata_groups = "companies, firewalls, servers, firewall_external, dnsservers, ${var.team_name}"
    metadata_company_info = jsonencode(var.team_info)
    child_networks = { # --> created networks
        dmz = {
            name         = "${var.team_name}_dmz"
            cidr         = local.dmz_cidr
            dns_nameservers = local.team_dns_servers
            destinations = [local.soc_cidr, local.access_cidr, local.supervisory_cidr, local.field_cidr] # probably extend with other networks (such as building and facility)
        }
    }
}


module "soc-access" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-vmnets.git"

    # base network / parent network
    parent_network_id = module.dmz.networks["dmz"].network_id
    parent_subnet_id = module.dmz.networks["dmz"].subnet_id
    parent_cidr = module.dmz.networks["dmz"].cidr
    parent_dns_nameservers = local.team_dns_servers # local team dns server...
    parent_gateway_ip = cidrhost(module.dmz.networks["dmz"].cidr, module.dmz.networks["dmz"].host_index)

    firewall_name = "${var.team_name}_firewall_internal"
    firewall_image = var.images.server
    firewall_flavor = var.flavors.server
    metadata_groups = "companies, firewalls, servers, firewall_internal, ${var.team_name}"
    metadata_company_info = jsonencode(var.team_info)
    child_networks = { # --> created networks
        soc = {
            name = "${var.team_name}_soc"
            cidr = local.soc_cidr
            dns_nameservers = local.team_dns_servers
        }
        access = {
            name = "${var.team_name}_access"
            cidr = local.access_cidr
            dns_nameservers = local.team_dns_servers
            destinations = [local.supervisory_cidr, local.field_cidr]
        }
    }
}

module "supervisory" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-vmnets.git"

    # base network / parent network
    parent_network_id = module.soc-access.networks["access"].network_id
    parent_subnet_id = module.soc-access.networks["access"].subnet_id
    parent_cidr = module.soc-access.networks["access"].cidr
    parent_dns_nameservers = local.team_dns_servers # local team dns server...
    parent_gateway_ip = cidrhost(module.soc-access.networks["access"].cidr, module.soc-access.networks["access"].host_index)

    firewall_name = "${var.team_name}_firewall_ot"
    firewall_image = var.images.server
    firewall_flavor = var.flavors.server
    metadata_groups = "companies, firewalls, servers, firewall_ot, ${var.team_name}"
    metadata_company_info = jsonencode(var.team_info)
    child_networks = { # --> created networks
        supervisory = {
            name = "${var.team_name}_supervisory"
            cidr = local.supervisory_cidr
            dns_nameservers = local.team_dns_servers
            destinations = [local.field_cidr]
        }
    }
}

module "field" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-vmnets.git"

    # base network / parent network
    parent_network_id = module.supervisory.networks["supervisory"].network_id
    parent_subnet_id = module.supervisory.networks["supervisory"].subnet_id
    parent_cidr = module.supervisory.networks["supervisory"].cidr
    parent_dns_nameservers = local.team_dns_servers #["10.0.0.1"] # local team dns server...
    parent_gateway_ip = cidrhost(module.supervisory.networks["supervisory"].cidr, module.supervisory.networks["supervisory"].host_index)

    firewall_name = "${var.team_name}_firewall_field"
    firewall_image = var.images.server
    firewall_flavor = var.flavors.server
    metadata_groups = "companies, firewalls, servers, firewall_field, ${var.team_name}"
    metadata_company_info = jsonencode(var.team_info)
    child_networks = { # --> created networks
        field = {
            name = "${var.team_name}_field"
            cidr = local.field_cidr
            dns_nameservers = local.team_dns_servers
        }
    }
}

output "networks" {
    value = merge(module.dmz.networks, module.soc-access.networks, module.supervisory.networks, module.field.networks)
}