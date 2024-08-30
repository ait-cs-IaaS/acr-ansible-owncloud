# Sources

## Build Hosts
source "openstack" "builder" {
  flavor                  = "${var.flavor}"
  # floating_ip_network     = "${var.floating_ip_pool}"
  image_name              = "${var.timestamp_image ? replace(format("%s-%s", var.image_name, timestamp()), ":", "-") : var.image_name}"
  network_discovery_cidrs = "${var.network_discovery_cidrs}"
  security_groups         = ["${var.security_group}"]
  ssh_ip_version          = "4"
  ssh_username            = "${var.build_user}"
  # ports                   = ["c2d25575-7969-48af-8954-24f7532e637e"]

  source_image_filter {
    filters {
      name = "${var.base_image}"
    }
    most_recent = true
  }
}