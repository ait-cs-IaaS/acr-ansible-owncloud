from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {
            "extract_floating_ip": self.extract_floating_ip,
            "extract_ip_dict": self.extract_ip_dict,
        }

    def extract_floating_ip(self, addresses, **kwargs):

        floating_ip = get_floating_ip(addresses)

        return floating_ip

    def extract_ip_dict(self, addresses):

        ip_addresses_dict = {}

        for key, value in addresses.items():
            if key != "internet":
                key = key.split("_")[1]
            ip_addresses_dict[key] = value[0].get("addr")

        return ip_addresses_dict


# Define a function to extract floating IPs from any subdictionary
def get_floating_ip(data):
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("OS-EXT-IPS:type") == "floating":
                    return item["addr"]
        elif isinstance(value, dict):
            ip_address = get_floating_ip(value)
            if ip_address:
                return ip_address
    return None
