variable "internet_cidr" { type = string }
variable "internet_network_id" { type = string }
variable "internet_subnet_id" { type = string }

#IMAGES
variable "images" { type = map(string) }

#FLAVORS
variable "flavors" { type = map(string) }

#####################
### CONFIGURATION ###
#####################
variable "attackers" {
  type        = map(number)
  description = "Map containing internet host address indices for each attacker"
  default = {
    # with cidr 240.64.0.0/10
    1 = 20000  # 240.64.78.33
    2 = 400000 # 240.70.26.129
    3 = 600000 # 240.73.39.193
    4 = 800000 # 240.76.53.1
    5 = 800100 # ?
  }
}

variable "attack_mates" {
  type        = map(number)
  description = "Map containing internet host address indices for each attackmate"
  default = {
    # with cidr 240.64.0.0/10
    1 = 500000
    # 2 = 700000 
    # 3 = 1100000 
    # 4 = 1550000 
  }
}