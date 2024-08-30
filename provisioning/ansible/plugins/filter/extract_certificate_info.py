def extract_certificate_info(hosts_dict, domains):
    """
    Extracts certificate information from a dictionary of hosts and organizes it into a structured format.

    Args:
        hosts_dict (dict): A dictionary containing the hostnames and the respective certificate information.
        domains (dict): A dictionary containing information about domains.

    Returns:
        list: A list containing certificate information for all hosts.
    """

    # Initialize an empty list to store certificate information
    certs = []

    for ansible_hostname, host_domains in hosts_dict.items():

        for host_domain in host_domains.values():

            if host_domain.get("certificate", False):

                # Extract certificate information from the host_domain dictionary
                cert_info = host_domain.get("certificate_info", {})

                # Get domain based on domain_id
                domain_id = host_domain.get("domain_id")
                domain = domains.get(domain_id, {}).get("domain", domain_id)

                hostname = host_domain.get("hostname")
                common_name = host_domain.get(
                    "common_name", (f"{hostname}.{domain}" if hostname else domain)
                )

                # Extract alternative names from the certificate information and add the common name
                cert_alt_names = cert_info.get("subject_alt_name", [])
                cert_alt_names.append(f"DNS:{common_name}")

                # Extract alternative names from host aliases and add them to cert_alt_names
                for alias in host_domain.get("aliases", []):
                    if isinstance(alias, dict) and alias.get("certificate_alt_name"):
                        alias_hostname = alias.get("hostname")
                        alias_fqdn = (
                            f"{alias_hostname}.{domain}" if alias_hostname else domain
                        )
                        new_alt_name = f"{alias.get('certificate_alt_name')}:{alias_fqdn}"

                        if new_alt_name not in cert_alt_names:
                            cert_alt_names.append(new_alt_name)

                # Create a dictionary containing processed certificate information
                processed_info = {
                    "common_name": common_name,
                    "name": host_domain.get("name", f"{hostname}.{domain_id}"),
                    "subject_alt_name": cert_alt_names,
                    "country": cert_info.get("country"),
                    "state": cert_info.get("state"),
                    "locality": cert_info.get("locality"),
                    "organization": cert_info.get("organization"),
                    "organization_unit": cert_info.get("organization_unit"),
                    "email": cert_info.get("email"),
                    "host": ansible_hostname,
                }

                # Remove any None values from the processed_info dictionary
                processed_info = {
                    key: value for key, value in processed_info.items() if value
                }

                # Append the processed certificate to certs list
                certs.append(processed_info)

    # Return the list containing certificate information for all hosts
    return certs


class FilterModule:
    """
    Ansible filter module for extracting certificate information from hosts.

    This filter module integrates with Ansible to provide a custom filter, `extract_certificate_info`,
    which can be used in Ansible playbooks to extract and process certificate information from hosts.

    Example Usage in Ansible Playbook:
        - name: Process certificate info
          ansible.builtin.set_fact:
            cert_configs: "{{ _dns_hosts | extract_certificate_info(domains) }}"
    """

    def filters(self):
        return {"extract_certificate_info": extract_certificate_info}
