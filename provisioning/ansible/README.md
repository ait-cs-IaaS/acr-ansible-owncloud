# Ansible Provisioning

This Project can only be run using Ansible for Python3, due to the use of custom filters written in Python3.
Make sure you have the latest version of Ansible installed using Python3!

## Start working

1. Connect to the Cyber Range VPN
2. Activate your  `OpenStack RC file`: `source <file path>`
3. Configure your Ansible for this project `source activate`
4. Download the Ansible dependencies (if this is your first time or they have changed)
   1. Python Dependecies: `pip3 install -r requirements.txt`
   2. Role Dependencies: `ansible-galaxy install -r requirements.yml`

To leave the virtual Ansible environment execute `deactivate`.

## SSH Connections to Ansible hosts

The project setup assumes that OpenStack will not only be used for the end product, but also for development.
SSH Connections to Ansible hosts are established by using the designated `mgmthost` of your active OpenStack project as a proxy/jump host. Also the OpenStack inventory plugin is configured so that the private ip addresses for connecting to Ansible hosts (sadly this cannot be disabled via the command line at the moment). 

### SSH Connection Variables

The below variables can be used to alter the default SSH connection behavior.

| Variable name                   | Type    | Default | Description                                             |
| ------------------------------- | ------- | ------- | ------------------------------------------------------- |
| ait_ssh_use_proxy | bool | True | Switch to enable/disable usage of the proxy/jump host. |
| ait_ssh_key | path | ~/.ssh/cyberrange | The SSH key that should be used. Note that most SSH agents will also try other keys if this key fails. |
| ait_ssh_proxy_user | string | ubuntu | The username to authenticate the proxy connection with. |
| ait_ssh_proxy_host | string | `{{ hostvars['mgmthost'].openstack.public_v4 }}` | The host that should be used as the proxy server. By default we will use the public ip address of the `mgmthost` instance. |

#### Alternative Configurations Examples

##### Use a specific proxy host and user

```bash
# proxy with debian@172.0.1.1
ansible-playbook main.yml -e ait_ssh_proxy_user=debian -e ait_ssh_proxy_host=172.0.1.1
```

##### Use local VM instances

Sometimes you do not want or cannot connect to the OpenStack server and want to test your playbooks on local machines.
For this you will have to disable SSH proxying and define an additional local inventory, which should be stored outside of the repository.
Note that you might also have to configure some automatic groups (e.g., `employees`), which are usually defined by tags, or OpenStack related variables within this local inventory file.

```ini
# ~/local-inventories/test-hosts
[all]
# machines running on local VirtualBox for testing
management_share ansible_host=192.168.55.17
accounting_share ansible_host=192.168.55.18
```

To run playbooks on these local machines you have to set your local inventory and the `hosts` inventory file, which contains the group definitions. 

```bash
ansible-playbook -i ~/local-inventories/test-hosts ~i hosts -e ait_ssh_use_proxy=no main.yml
```


## Playbooks

Playbooks used to provision software to machines or groups of machines should be grouped by feature/purpose and placed in a directory under [./playbooks/deploy](./playbooks/deploy).
There always has to be a main playbook called `main.yml`, which contains or references all necessary plays for the feature/purpose.
Also all **plays and tasks** must have a meaningful name.

## Ansible Role Dependencies

Some playbooks depend on ansible roles. These roles have to be installed before running the playbooks.
This can be achieved with `ansible-galaxy`, also note that you must have the ansible provisioning environment activated in order for the correct roles directory be set.

```bash
source ./activate
ansible-galaxy install -r requirements
```

If your playbook uses an ansible role make sure that add it to the `requirements.yml`. 

