locals {
    dmz_cidr = cidrsubnet(var.global_dmz_cidr, 4, var.team_key)
    soc_cidr = cidrsubnet(var.global_soc_cidr, 4, var.team_key)
    access_cidr = cidrsubnet(var.global_access_cidr, 4, var.team_key)
    supervisory_cidr = cidrsubnet(var.global_supervisory_cidr, 4, var.team_key)
    field_cidr = cidrsubnet(var.global_field_cidr, 4, var.team_key)

    team_dns_servers = [cidrhost(local.dmz_cidr, 1)]
}