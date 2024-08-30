from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {"create_user": self.create_user}

    def create_user(self, user, **kwargs):
        # Default values
        user_object = {
            "first_name": "",
            "last_name": "",
            "username": "",
            "email": "",
            "email_user": "",
            "password": "",
            "password_salt": "",
            "smime": False,
            "ssh_key": False,
            "ssh_admin": False,
            "control_mail": False,
            "emailuser_is_email": False,
            "company": "",
            "company_domain": "",
            "horde_contact": False,
            "ot_admin": False,
            "grafana_admin": False,
            "supplypro_admin": False,
            "wp_role": "",
            "responsibilies": [],
            "group_emails": [],
            "contact_groups": [],
            "owncloud_groups": [],
            "owncloud_user": "",
            "samba_groups": [],
            "learners_groups": [],
        }

        # extract and apply defaults if passed in
        if defaults := kwargs.get("defaults", None):
            user_object.update(defaults)

        # Override generic user with given user
        user_object.update(user)

        user_object = setComposits(user_object)

        return user_object


def setComposits(user):
    user["username"] = user.get("username").replace(" ", "_").lower()
    if not user.get("username"):
        if user.get("last_name") and user.get("first_name"):
            # If username is not set the username is generated from the first and the last name:
            # e.g. John Doe -> doej
            user["username"] = (
                f"{ user.get('last_name', '').replace(' ', '_').lower() }{ user.get('first_name', '').lower()[0] }"
            )
        else:
            raise AnsibleFilterError(
                "Username undefined. Either set username or first_name and last_name."
            )

    if not user.get("owncloud_user"):
        user["owncloud_user"] = f"{user.get('company')}_{user.get('username')}"

    if not user.get("email"):
        if user.get("first_name") and user.get("last_name"):
            # If email is not set the email is generated from the first and the last name:
            # e.g. John Doe -> john.doe@company.com
            comp_email = f"{ user.get('first_name').replace(' ', '_').lower() }.{ user.get('last_name').replace(' ', '_').lower() }@{ user.get('company_domain') }"
        else:
            # if first name and last name are undefined, the email is generated using the username
            # e.g. doej -> doej@company.com
            comp_email = f"{ user.get('username').replace(' ', '_').lower() }@{ user.get('company_domain') }"
        user["email"] = comp_email

    if not user.get("email_user"):
        if user.get("emailuser_is_email"):
            user["email_user"] = user.get("email")
        elif not user.get("first_name"):
            user["email_user"] = user.get("username")
        else:
            user["email_user"] = user.get("email").split("@")[0]

    user["group_emails"].append(user.get("email"))

    if "ot" in (resp.lower() for resp in user.get("responsibilies")):
        user["grafana_admin"] = True
        user["ot_admin"] = True

    return user
