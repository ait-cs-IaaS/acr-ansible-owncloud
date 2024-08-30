from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {"extract_learners_users": self.extract_learners_users}

    def extract_learners_users(
        self,
        userlist: dict,
    ) -> list:
        """
        Extracts learners user data from a given userlist, including relevant metadata and VNC client information.

        Parameters:
            userlist (dict): Dictionary containing user data organized by sublists.

        Returns:
            list: List of dictionaries containing extracted learners' user data.
        """

        learners_users = {}
        control_teams = {}

        # Iterate through each sublist in userlist
        for sublist in userlist.values():
            # Iterate through each user in the sublist
            for user in sublist:
                # Retrieve user data
                novnc_user = user.get("novnc_user")
                novnc_password = user.get("novnc_password")
                learners_role = user.get("learners_role")
                first_name = user.get("first_name")
                last_name = user.get("last_name")
                email = user.get("email")
                learners_groups = user.get("learners_groups")
                mattermost_teams = {}
                mattermost_admin = user.get("mattermost_admin", False)

                # Check if user has novnc
                if user.get("novnc"):
                    # Create user object
                    user_object = {
                        "password": novnc_password,
                        "role": learners_role,
                        "meta": {
                            "control": user.get("role") == "control",
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "groups": learners_groups,
                            "mattermost": {"teams": mattermost_teams},
                            "mattermost_admin": mattermost_admin,
                        },
                    }

                    # Add mattermost teams and channels
                    if user.get("matermost_teams"):
                        for team in user.get("matermost_teams", []):
                            mattermost_channels = set(
                                ["support"]
                                + user.get("mattermost_channels", [])
                                + team.get("channels", [])
                            )
                            mattermost_teams[team] = {
                                "channels": list(mattermost_channels)
                            }
                    elif user.get("company"):
                        mattermost_channels = set(
                            ["support"] + user.get("mattermost_channels", [])
                        )
                        mattermost_teams[user.get("company")] = {
                            "channels": list(mattermost_channels)
                        }

                    # Add user object to learners_users dictionary
                    learners_users[novnc_user] = user_object

                    # Add VNC clients if not already present
                    vnc_clients = user.get("vnc_clients", {})
                    if not vnc_clients and user.get("host"):
                        vnc_clients[user.get("username")] = {
                            "target": user.get("host"),
                            "tooltip": f"{user.get('username')} client",
                            "username": user.get("username"),
                            "password": user.get("password"),
                        }
                    user_object["vnc_clients"] = vnc_clients

                    # Update control_teams dictionary with mattermost channels for non-control users
                    if not learners_role == "control":
                        for team, channels in mattermost_teams.items():
                            control_teams.setdefault(team, set()).update(channels)

        # Update mattermost teams for control users
        for _, user_data in learners_users.items():
            if user_data["meta"]["mattermost_admin"]:
                user_data["meta"]["mattermost"]["teams"] = {
                    team: {"channels": list(channels)}
                    for team, channels in control_teams.items()
                }

        return learners_users


def display_warning(msg):
    print(f"\033[95m\n[WARNING] {msg}\033[0m")
