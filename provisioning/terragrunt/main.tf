terraform {
  backend "http" {}
}

module "fake-internet" {
    source = "git@github.com:ait-cs-IaaS/terraform-openstack-inet.git"
    public_router_name = var.public_router
    dns_image = var.images.server
    dns_flavor = var.flavors.server
}

module "fake-internet-hosts" {
    source = "./internet-hosts"
    internet_cidr = module.fake-internet.cidr
    internet_network_id = module.fake-internet.network_id
    internet_subnet_id = module.fake-internet.subnet_id

    # BASE IMAGE and FLAVORS (These need to be passed, because they change depending on deploying on our Range or on OVH)
    images = var.images
    flavors = var.flavors
}

# INFRASTRUKTUR FÜR JEDES TEAM INS FAKE-INTERNET ANHÄNGEN
module "team-infrastructure" {
    source = "./team-infrastructure"
    for_each = { for key,team in var.teams : format("%.4d",key) => team } # transform the list var.teams to a map and PRESERVE the order 0

    #TEAM name
    team_name = each.value.name
    team_key  = each.key
    team_info = each.value

    #INTERNET (and lanturtle) Information 
    internet_network_id = module.fake-internet.network_id
    internet_subnet_id = module.fake-internet.subnet_id
    internet_cidr = module.fake-internet.cidr
    internet_host_index = each.key + 162*10 # ip address, that has the external firewall of the team in the internet --> Internetanschlusspunkt.
    internet_dns_ip = module.fake-internet.dns
    internet_gateway_ip = module.fake-internet.gateway_ip
    lanturtle_internet_host_index = each.key + 501017

    # BASE IMAGE and FLAVORS (These need to be passed, because they change depending on deploying on our Range or on OVH)
    images = var.images
    flavors = var.flavors
}

module "mgmthosts" {
    source = "./mgmthosts"
    
    #INTERNET Information
    internet_network_id = module.fake-internet.network_id
    internet_subnet_id = module.fake-internet.subnet_id
    internet_cidr = module.fake-internet.cidr
    fip_pool = var.fip_pool

    all_team_networks = local.all_team_networks
    teams = var.teams

    # BASE IMAGE and FLAVORS (These need to be passed, because they change depending on deploying on our Range or on OVH)
    images = var.images
    flavors = var.flavors
}