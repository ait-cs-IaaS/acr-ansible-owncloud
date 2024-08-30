# User Management

> Category: Deploy



The user management playbook orchestration provides means of generating and distributing ssh-keys, creating necessary user accounts on the remote hosts. 



## 1. Manage ssh-keys for all users

**Hosts:** localhost
**Roles:** -

The purpose of this playbook is to generate ssh-keys for all users, as defined as game_users in /group_vars/all/users.yml:

```yml
game_users: |
    {{
        { 'control': control, 'malware': malware_ssh_user } | combine(
          (teams | combine(
              employees
            )
          ))
        | add_user_ids
        | add_usernames(target='name')
    }}
```

game_users comprise the control user, the malware_ssh_user as well as all user definitions from /group_vars/all/players.yml and /group_vars/all/employees.yml. Two custom filters are applied to extract the user_ids and the usernames.



**Steps of playbook:**

1. Creates directories for all game_users
2. Checks if ssh-key pair exists, if not, generates RSA ssh-key pairs (4096 Bit) for all game_users [ansible openssl-keypair]

The keys are stored in the following structure:

```bash
data
├── ssh-keys
│   ├── *user_ids*
```





## 2. Manage users for all hosts

**Hosts:** all, !firewalls
**Roles:** 	 

- grog.user
- grog.sudo
- grog.authorized-key



The following user-lists are used to create local accounts with corresponding ssh-keys on the respective hosts:

**game_users_hashed_pws** consists of all game_users, but with encrypted password (SHA512)

**all_users** depicts standard users present on all hosts such as the 'tec' user, whom is granted ssh-access to all machines. Users belonging to this group is defined in /group_vars/internal_net/users.yml as well as in /group_vars/sec_net/users.yml.  

**host_users:** for each relevant host there is a configuration file in /host_vars/*hostname*/users.yml. In this file specific users are selected from the game_users_hashed_pws list to be active users for the respective host. In the following example, the user 'm06' which corresponds to *Wolfgang Weiss* (see /group_vars/all/employees.yml) is selected from the hased password list to be an active user on the host:

```yml
host_users:
    - | 
        {{ 
            game_users_hashed_pws['m06'] 
            | authorized_key_users(ssh_keys_base_path, use_user_key=True)
            | sudo_config  
        }}
```

**group_users** can be used to specify users per group of hosts



**Playbook description:**

- **grog.user** creates user accounts
- **grog.sudo** manages sudo priviledges, by adding and editing sudoers.d files per specified user.

- **grog.authorized-key** manages authorized-keys



**Additional tasks of the playbook:**

1. Creates .ssh-folder per user if necessary
2. Copies the previously generated SSH private and public key to remote host







