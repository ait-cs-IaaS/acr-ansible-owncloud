# make a flat list out of all networks created for the different teams.
locals{
    all_team_networks = merge([
        for team_key, team_value in var.teams : {
            for key, value in module.team-infrastructure[format("%.4d",team_key)].networks : "${team_value.name}_${key}" => { #format(...) is necessary to transform the keys from the array of var.teams to strings of "0000", "0001", and so on.
                name = value.name
                cidr = value.cidr
                network_id = value.network_id
                subnet_id = value.subnet_id
            }
        }
    ]...)
}