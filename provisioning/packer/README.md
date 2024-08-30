# Custom Image Provisioning

## Start working

1. Connect to the OpenStack VPN
2. Activate your  `OpenStack RC file`: `source <file path>`

## Prerequisites

1. An external network(Self-Service Network)
2. A internal network to host a build VM
3. Required base images uploaded (e.g., ubuntu, debian)
4. The latest packer version from https://packer.io

## Building an images

1. Change to the image directory: cd `<image directory>`
2. Create a var file to configure the build. (See `default.json` for an example configured for the AECID testbed)
3. [Optional] ansible-galaxy role install --role-file playbook/requirements.yml --roles-path playbook/roles/
4. Build the image: packer: `packer build -var-file=<var file> .`  *!!! The dot at the end is important !!!*
5. Repeat 1-3 for all required images

