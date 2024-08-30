public_router        = "cyberrange-router"
#provider_net_uuid    = "b2c02fdc-ffdf-40f6-9722-533bd7058c06"
#provider_subnet_uuid = "1a6c6b72-88e9-4e94-ac8b-61e6dbc4792c"

fip_pool   = "Ext-Net"


images = {
    server = "Ubuntu 20.04"
    client = "cr-client-ubuntu-2004"
    elk    = "Ubuntu 20.04"
}

flavors = {
    server = "d2-4"
    client = "b2-7"
    elk    = "b2-7"
}