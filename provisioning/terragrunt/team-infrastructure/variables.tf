#TEAM INFORMATION
variable "team_name" { type = string }
variable "team_key" { type = string }
# TEAMS VARIABLE
variable "team_info" {
  type = object({
      name = string
      domain       = string
      display_name = string
      password     = string
      cloud        = bool
    })
}

#INTERNET INFORMATION
variable "internet_network_id" { type = string }
variable "internet_subnet_id" { type = string }
variable "internet_cidr" { type = string }
variable "internet_host_index" { type = number }
variable "internet_dns_ip" { type = list(string) }
variable "internet_gateway_ip" {type = string}
variable "lanturtle_internet_host_index" { type = number }


#IMAGES
variable "images" { type = map(string) }

#FLAVORS
variable "flavors" { type = map(string) }

#NETWORK CIDRS
variable "global_dmz_cidr" {
  type = string
  default = "10.0.0.0/20"
}

variable "global_soc_cidr" {
  type = string
  default = "172.16.32.0/20"
}

variable "global_access_cidr" {
  type = string
  default = "172.16.0.0/20"
}

variable "global_supervisory_cidr" {
  type = string
  default = "192.168.0.0/20"
}

variable "global_field_cidr" {
  type = string
  default = "192.168.32.0/20"
}