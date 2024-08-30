variable "internet_network_id" { type = string }
variable "internet_subnet_id" { type = string }
variable "internet_cidr" { type = string }

#FIP POOL
variable "fip_pool" { type = string }


# TEAMS VARIABLE
variable "teams" {
  type = list(
    object({
      name = string
    })
  )
}

# TEAMS INFRASTRUCTURE VARIABLE
variable "all_team_networks" {
  type = map(
    object({
      name = string
      cidr = string
      network_id  = string
      subnet_id  = string
    })
  )
  default = {}
}

#IMAGES
variable "images" { type = map(string) }

#FLAVORS
variable "flavors" { type = map(string) }
