locals {
    mgmt_networks = { for key, value in var.all_team_networks : key => value }
    learners_networks = { for key, value in var.all_team_networks : key => value if endswith(key, "soc") || endswith(key, "access") || endswith(key, "supervisory")}
    control_networks = { for key, value in var.all_team_networks : key => value if endswith(key, "soc") }
    mailgin_networks = { for key, value in var.all_team_networks : key => value if endswith(key, "dmz") }
    venjix_networks = { for key, value in var.all_team_networks : key => value if endswith(key, "soc") }
}