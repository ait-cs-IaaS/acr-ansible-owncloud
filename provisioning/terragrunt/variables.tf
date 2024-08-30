# TEAMS VARIABLE
variable "teams" {
  type = list(
    object({
      name         = string
      domain       = string
      display_name = string
      password     = string
      cloud        = bool
    })
  )
}

#########################
### OVH CONFIGURATION ###
#########################

#PUBLIC ROUTER
variable "public_router" { type = string }

#IMAGES
variable "images" {
  type = map(string)
  default = {
    server = "Ubuntu 24.04"
    elk    = "Ubuntu 24.04"
    client = "cr-client-ubuntu-2404-update-2024-07-31"
  }
}

#FLAVORS
variable "flavors" {
  type = map(string)
  default = {
    server = "d2-2"
    client = "d2-8"
    elk    = "d2-8"
  }
}

#FIP POOL
variable "fip_pool" {
  type    = string
  default = "CBT-DEV-provider-network"
}
