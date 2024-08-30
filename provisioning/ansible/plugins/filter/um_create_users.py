import hashlib
from collections import defaultdict
from ansible.errors import AnsibleFilterError
import copy


class FilterModule(object):
    def filters(self):
        return {
            "create_users": self.create_users,
            "create_group_emails": self.create_group_emails,
        }

    def create_users(
        self,
        userlist_input: list,
        defaults: dict = {},
        role: str = "",
        companies: dict = {},
    ) -> list:
        """
        Custom Ansible Jinja filter to create user objects based on input data and provided keyword arguments.

        Parameters:
            - userlist_input (list): Input data containing user information.
            - defaults (dict, optional): Default user information to populate user objects. Default is an empty dictionary.
            - role (string, optional): Role information to assign to user objects. Default is an empty string.
            - companies (dict, optional): Dictionary containing company information for user creation. Default is an empty dictionary.

        Returns:
            - list: A list of user objects created based on the input data and provided keyword arguments.

        This function creates user objects based on the input data and specified keyword arguments.
        If companies are provided, it creates user objects for each company, incorporating company-specific information.
        Otherwise, it creates user objects with global settings.
        """

        if not isinstance(userlist_input, list):
            raise AnsibleFilterError(
                f"[Error] Expected a list as input, but got {type(userlist_input)} {userlist_input}"
            )
        if not isinstance(defaults, dict):
            raise AnsibleFilterError(
                f"[Error] Expected a dict as defaults input, but got {type(defaults)} {defaults}"
            )
        if not isinstance(role, str):
            raise AnsibleFilterError(
                f"[Error] Expected a string as role input, but got {type(role)} {role}"
            )
        if not isinstance(companies, dict):
            raise AnsibleFilterError(
                f"[Error] Expected a dict as companies input, but got {type(companies)} {companies}"
            )

        userlist = []

        userlist_input = self.add_enumerated_users(userlist_input)

        # Populate base object with given defaults
        user_info = defaults

        # Assign role
        user_info["role"] = role

        if companies:
            # If companies are given, repeat user creation per company
            for _, company_info in companies.items():
                user_info.update(
                    {
                        "company": company_info.get("name", ""),
                        "domain": company_info.get("domain", ""),
                        "password": company_info.get("password", ""),
                        "mailserver": f"{company_info.get('name', '')}_mail",
                    }
                )

                userlist += self.create_userlist(userlist_input, user_info)

        else:
            # Set mailserver to global
            user_info.update(
                {
                    "mailserver": "global_mail",
                }
            )
            userlist = self.create_userlist(userlist_input, user_info)

        return userlist

    def add_enumerated_users(self, dictlist) -> list:
        """
        Replaces a dict where 'gen_enumerate' is given with the respective number of dicts.

        This function iterates over the provided user list, and creates a number of dicts based on the 'gen_enumerate' key. The enumerating key can be specified by 'gen_enumerate_key' or its default value 'username'.

        Args:
            dictlist (list): A list containing user dictionaries.

        Returns:
            list: A list of dictionaries representing the newly created users.

        Example:
            input: [{'username': 'csirt', 'gen_enumerate': 3}]
            output: [{'username': 'csirt1', 'gen_enumerate': 3}, {'username': 'csirt2', 'gen_enumerate': 3}, {'username': 'csirt3', 'gen_enumerate': 3}]
        """

        updated_dictlist = []
        for item in dictlist:
            if "gen_enumerate" in item:
                gen_key = item.get("gen_enumerate_key", "username")
                gen_count = item["gen_enumerate"]
                for i in range(1, gen_count + 1):
                    new_item = item.copy()
                    new_item[gen_key] = f"{new_item[gen_key]}{i}"
                    updated_dictlist.append(new_item)
            else:
                updated_dictlist.append(item)
        return updated_dictlist

    def create_group_emails(self, userlist) -> list:
        """
        Creates group email users based on the provided user list.

        This function iterates over the provided user list, extracts group email information,
        and creates new group email users. It ensures that group email users are not duplicated and excludes any group emails specified to be ignored.

        Args:
            userlist (dict): A dictionary containing lists of user dictionaries.

        Returns:
            list: A list of dictionaries representing the newly created group email users.
        """

        if not isinstance(userlist, dict):
            raise AnsibleFilterError(
                f"[Error] Expected a dict as input, but got {type(userlist)} {userlist}"
            )

        # Flatten the userlist into a single list of users
        users = [user for sublist in userlist.values() for user in sublist]
        group_emails = []

        # Extract emails of users marked to be ignored
        ignore_emails = {
            user["email"] for user in users if user.get("role") == "group_email"
        }

        # Iterate over each user in the user list
        for user in users:
            user_group_emails = user.get("group_emails", [])

            # Iterate over group emails for the current user
            for user_group_email in user_group_emails:
                if user_group_email not in ignore_emails:
                    # Construct information for the new group email user
                    group_info = {
                        "role": "group_email",
                        "first_name": user_group_email.split("@")[0],
                        "last_name": user.get("company"),
                        "display_name": f"{user_group_email.split('@')[0]} {user.get('company')}",
                        "email": user_group_email,
                        "smime": user.get("smime", False),
                        "company": user.get("company"),
                        "mailserver": user.get("mailserver"),
                        "email_user": user_group_email.split("@")[0],
                        "username": user_group_email.split("@")[0],
                        "password": user.get("password"),
                        "control_mail": True,
                        "contact_groups": user.get("contact_groups", []),
                    }

                    # Create the new group email user
                    new_group_email_user = self.new_user(group_info)
                    group_emails.append(new_group_email_user)
                    ignore_emails.add(user_group_email)

        return group_emails

    def create_userlist(self, userlist_input: dict, user_info: dict):
        """
        Choreographs the creation of user 'objects'

        Args:
            userlist_input (dict): Input data containing user information.
            user_info (dict): Input data containing company or additional information.

        Returns:
            list: A list of dictionaries representing the newly created users.
        """

        userlist = []
        indicies_holder = defaultdict(int)

        # Iterate through input list
        for user_params in userlist_input:

            # Ensure there is no propagation of user info from previously generated users
            c_user_info = copy.deepcopy(user_info)

            # Merge defaults with given parameters
            c_user_info.update(user_params)

            host_group = c_user_info.get("host_group", None)
            if host_group:
                indicies_holder[host_group] += 1

            # Create new user Object
            new_user = self.new_user(c_user_info, indicies_holder[host_group])

            # Append to output list
            userlist.append(new_user)

        return userlist

    def new_user(self, user_info, user_index=0):
        user = {
            "role": user_info.get("role", ""),
            "first_name": user_info.get("first_name", ""),
            "last_name": user_info.get("last_name", ""),
            "name": user_info.get("username", ""),
            "username": user_info.get("username", ""),
            "display_name": user_info.get("display_name", ""),
            "email": user_info.get("email", ""),
            "email_user": user_info.get("email_user", ""),
            "password": user_info.get("password", ""),
            "password_salt": user_info.get("password_salt", ""),
            "smime": user_info.get("smime", False),
            "ssh_key": user_info.get("ssh_key", False),
            "ssh_admin": user_info.get("ssh_admin", False),
            "control_mail": user_info.get("control_mail", False),
            "company": user_info.get("company", ""),
            "domain": user_info.get("domain", ""),
            "horde_contact": user_info.get("horde_contact", False),
            "ot_admin": user_info.get("ot_admin", False),
            "sudo": user_info.get("sudo", {}),
            "grafana_admin": user_info.get("grafana_admin", False),
            "supplypro_admin": user_info.get("supplypro_admin", False),
            "wp_role": user_info.get("wp_role", ""),
            "group_emails": user_info.get("group_emails", []),
            "contact_groups": user_info.get("contact_groups", []),
            "owncloud_groups": user_info.get("owncloud_groups", []),
            "owncloud_user": user_info.get("owncloud_user", ""),
            "samba_groups": user_info.get("samba_groups", []),
            "learners_groups": user_info.get("learners_groups", ["extra"]),
            "learners_role": user_info.get("learners_role"),
            "mattermost_channels": user_info.get("mattermost_channels", ["support"]),
            "mattermost_admin": user_info.get("mattermost_admin", False),
            "mailserver": user_info.get("mailserver", ""),
            "host": user_info.get("host", []),
            "desktop_files": user_info.get("desktop_files", []),
            "wp_role": user_info.get("wp_role", ""),
        }

        # Allow additional fields provided by defaults
        user.update(user_info)

        self.add_company_information(user, user_info)
        self.generate_email(user)
        self.generate_email_user(user)
        self.generate_username(user)
        self.generate_salt(user)
        self.set_host_information(user, user_index)
        self.set_novnc_information(user)
        self.set_ssh_information(user)
        self.set_desktop_files(user)
        self.set_sudo_config(user)
        self.set_shell(user, user_info)

        return user

    def set_sudo_config(self, user):
        """
        Process sudo config.
        """
        if not user.get("sudo") and user.get("ssh_admin"):

            user["sudo"] = {
                    "hosts": "ALL",
                    "as": "ALL:ALL",
                    "commands": "ALL",
                    "nopasswd": "yes"
                }

    def add_company_information(self, user, user_info):
        """
        Process company-specific information for the user.
        """
        if user.get("company"):
            user["contact_groups"] = list(
                set(user_info.get("contact_groups", []) + [user.get("company")])
            )

            for i, group_email in enumerate(user.get("group_emails")):
                if "@" not in group_email:
                    user["group_emails"][i] = f"{group_email}@{user.get('domain')}"

    def generate_email(self, user):
        """
        Generate email for the user if not provided.
        """
        if user.get("email"):
            if not user.get("domain"):
                user["domain"] = user.get("email").split("@")[1]
        else:
            if not user.get("domain"):
                user["domain"] = "cyberrange.at"
            if user.get("first_name") and user.get("last_name"):
                user["email"] = (
                    f"{user.get('first_name').replace(' ', '_').lower()}.{user.get('last_name').replace(' ', '_').lower()}@{user.get('domain')}"
                )
            else:
                user["email"] = (
                    f"{user.get('username').replace(' ', '_').lower()}@{user.get('domain')}"
                )

    def generate_email_user(self, user):
        """
        Process email username for the user.
        """
        if not user.get("email_user"):
            if user.get("mailserver") == "global_mail":
                user["email_user"] = user.get("email")
            else:
                user["email_user"] = user.get("email").split("@")[0]

    def generate_username(self, user):
        """
        Generate username for the user if not provided.
        """
        if not user.get("username"):
            username = (
                user.get("last_name").lower() + user.get("first_name").lower()[:1]
            ).replace(" ", "")
            user["username"] = username or user.get("email").split("@")[0]
        elif not user.get("first_name") and not user.get("last_name"):
            user["first_name"] = user.get("username")

        if not user.get("name"):
            user["name"] = user.get("username")

        if not user.get("owncloud_user"):
            user["owncloud_user"] = user.get("username")

        if not user.get("display_name"):
            user["display_name"] = (
                f"{user.get('first_name')} {user.get('last_name')} {user.get('company')} "
            ).replace("  ", " ")

    def generate_salt(self, user):
        """
        Generate a reproduceable/deterministic salt based on the username.
        -- don't do this at home ---
        """

        if not user.get("password_salt"):
            username = user.get("username")
            hashed_username = hashlib.sha256(username.encode()).hexdigest()
            salt = int(hashed_username, 16)

            user["password_salt"] = salt % 1000000000000

    def set_host_information(self, user, user_index):
        """
        Process host information for the user.
        """
        company = user.get("company", "")
        company_prefix = f"{company}_" if company else ""

        if host := user.get("host"):
            host = f"{company_prefix}{host}"

        elif host_group := user.get("host_group", ""):
            host = f"{company_prefix}{host_group}_{user_index}"

        user["host"] = host

    def set_novnc_information(self, user):
        """
        Process novnc information for the user.
        """
        if user.get("novnc", False):
            company = user.get("company", "")
            company_prefix = f"{company}_" if company else ""

            user["novnc_user"] = f"{company_prefix}{user.get('username')}"
            user["novnc_password"] = user.get(
                "novnc_password", user.get("password", "password")
            )
            if not user.get("learners_role"):
                user["learners_role"] = "participant"

    def set_ssh_information(self, user):
        """
        Add ssh key information to the user.
        """

        if user.get("ssh_key", False):
            company = user.get("company", "")
            company_prefix = f"{company}/" if company else ""
            user["ssh_key_path"] = f"{company_prefix}{user.get('username')}/"

    def set_desktop_files(self, user):
        """
        Add desktop files list
        """

        if not user.get("desktop_files"):
            desktop_files_list = ["all"]
            desktop_files_list += user.get("user_groups", [])
            user["desktop_files"] = desktop_files_list

    def set_shell(self, user, user_info):
        """
        Add shell to ssh_admins
        """

        if user.get("ssh_admin"):
            user["shell"] = user_info.get("shell", "/bin/bash")


def display_warning(msg):
    print(f"\033[95m\n[WARNING] {msg}\033[0m")
