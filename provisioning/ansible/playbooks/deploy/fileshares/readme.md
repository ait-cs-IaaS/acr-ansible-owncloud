# Samba Shares

> Category: Deploy


## 1. Setup and configure samba shares

**Hosts:** shares
**Roles:** 

- **grog.group**
  This role uses a provided group list which are then created on the host. In the case of the samba-shares, these lists are defined in the respective configuration files such as: /host_vars/management_share/samba.yml

  ```yml
  group_list_host:
    - name: management_r
    - name: management_w
    - name: reports_r
    - name: reports_w
  ```

  

- **grog.user**
  The grog.user-role uses the user_list_host to create the required user accounts, which is defined in /group_vars/shares/samba.yml where the samba_users_dict is converted to the final list.

  ```yml
  user_list_host: |
  	{{ (samba_users_dict | add_usernames(target='name') | 	
  	encrypt_passwords(hashtype='sha512')).values() | list  }}
  ```

  The user information is gathered in the corresponding host_vars, /host_vars/management_share/samba.yml, where the samba_clients_employees_dict provides selected employees from /group_vars/all/employees.yml und combines the entries with specific samba groups, defined in the samba_settings dict. 

  ```yml
  samba_users_dict: |
  	{{ samba_clients_employees_dict | combine(samba_settings, recursive=True) }}
  
  samba_clients_employees_dict:
    m01: "{{ employees.m01 }}"
    m02: "{{ employees.m02 }}"
    ...
  
  samba_settings:
    m01:
      groups: 
        - management_r
        - management_w
        - reports_r
        - reports_w
    m02:
      groups: 
        - management_r
        - management_w
        - reports_r
        - reports_w
    ...
  ```

  

- **samba**

  General samba configuration is defined using the variables in /group_vars/shares/samba.yml. Within this role, samba is installed and configured and the access for samba users is managed.



**Additional tasks of the playbook:**

1. Creates folder structure for files to be copied to the shares
2. Copies defined files to shares 



These files are e.g. defined as follows:

```yml
smb_extra_files_base: files/accounting

smb_extra_files:
  Billing:
    - src: Billing
      directory: true
      recursive: yes
      employee_id: m03
  Customers:
    - src: Customers
      employee_id: m03
      directory: true
      recursive: yes
```

Where smb_extra_files_base depicts the source folder on the ansible orchestration machine. The first layer of smb_extra_files represents the target share name of the remote server. By using recursive mode, the directory and all files within are copied to the server with the default settings and ownership, provided in this dict. It can also be specified using an owner attribute. Per default, recursive is set to false, resulting in copying only the corresponding file.

