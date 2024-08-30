from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {"select_users": self.select_users}

    def select_users(
        self,
        userlist: dict,
        filter: dict = {},
        returns: list = [],
        unique: bool = False,
        single: bool = False,
    ) -> list:
        """
        Custom Ansible Jinja filter to select users from a given userlist based on specified filters and return keys.

        Parameters:
            - userlist (dict): A dictionary containing lists of users.
            - filter (dict): Dictionary containing filter criteria.
            - returns (list, optional): List of keys to return for each user. Default is an empty list.
            - unique (bool, optional): Flag indicating whether to return unique values. Default is False.
            - single (bool, optional): Flag indicating whether to return only the first item. Default is False.

        Returns:
            - list: A list of users selected based on the provided filters and return keys.
            - (dict: if single-flag is set) 

        This function iterates over the userlist and applies filters based on the provided filter criteria.
        It then selects the specified return keys for each user and returns the resulting list of users.
        """

        if isinstance(filter, dict) == False:
            raise AnsibleFilterError(
                f"[Error] Expected a dict as filter input, but got {type(filter)}: ------------- {filter}"
            )
        if isinstance(returns, list) == False:
            raise AnsibleFilterError(
                f"[Error] Expected a list of strings as input, but got {type(returns)}: ------------- {returns}"
            )
        if isinstance(unique, bool) == False:
            raise AnsibleFilterError(
                f"[Error] Expected a boolean as unique value, but got {type(unique)}: ------------- {unique}"
            )

        if isinstance(userlist, list) == True:
            return_list = userlist
        elif isinstance(userlist, dict) == True:
            # Flatten the userlist dictionary into a single list
            return_list = [user for sublist in userlist.values() for user in sublist]
        else:
            raise AnsibleFilterError(
                f"[Error] Expected a dict or list as input, but got {type(userlist)}: ------------- {userlist}"
            )

        for filter_name, filter_value in filter.items():
            filtered_list = []

            # Allows using '|' to define logical ORs in filter values
            # e.g. users | select_users(filter={'role': 'control | csirt', 'company': company_name + '| undefined'}, returns=['username'])
            if isinstance(filter_value, str):
                filter_values = [value.strip() for value in filter_value.split("|")]
            else:
                filter_values = [filter_value]

            # Apply filter per user
            for user in return_list:

                for _filter_value in filter_values:

                    if _filter_value == "defined":
                        if user.get(filter_name):
                            filtered_list.append(user)

                    elif _filter_value == "undefined":
                        if not user.get(filter_name):
                            filtered_list.append(user)

                    # Check if the filter value is a list
                    elif isinstance(user.get(filter_name), list):
                        # Allow NOT operator
                        if isinstance(_filter_value, str) and _filter_value.startswith(
                            "!"
                        ):
                            if _filter_value.split("!")[1] not in user.get(filter_name):
                                filtered_list.append(user)

                        # If the given value is a list, it returns true if ANY of the elements match
                        if isinstance(_filter_value, list):
                            if bool(
                                set(user.get(filter_name, [])) & set(_filter_value)
                            ):
                                filtered_list.append(user)
                        else:
                            if _filter_value in user.get(filter_name):
                                filtered_list.append(user)

                    # Check if the filter value is a boolean
                    elif isinstance(user.get(filter_name), bool):
                        if user.get(filter_name) == bool(_filter_value):
                            filtered_list.append(user)
                    else:

                        # Handle non-list and non-boolean filter values
                        if _filter_value.startswith("!"):
                            if (
                                user.get(filter_name).upper()
                                != (_filter_value.split("!")[1]).upper()
                            ):
                                filtered_list.append(user)
                        else:
                            if user.get(filter_name).upper() == _filter_value.upper():
                                filtered_list.append(user)

            # Update return_list with the filtered list for the current filter
            return_list = filtered_list

        # Limit output if returns are provided
        if returns:

            if unique and len(returns) > 1:
                display_warning(
                    f"Incompatible number of return values. The 'unique' filter is only possible if the length of 'returns' is 1 but {len(returns)} were given."
                )

            if not unique and len(returns) == 1:
                return_list = [user[returns[0]] for user in return_list]
            elif not unique or len(returns) > 1:
                # Construct a new list of dictionaries containing only the specified return keys
                return_list = [
                    {key: user[key] for key in returns} for user in return_list
                ]
            else:
                # Construct a new list containing unique values from the specified return keys
                _return_list = [user[key] for key in returns for user in return_list]
                if all(isinstance(item, list) for item in _return_list):
                    # Merge all sublists
                    return_list = list(
                        set(item for sublist in _return_list for item in sublist)
                    )
                else:
                    # Remove duplicates from a list of strings
                    return_list = list(set(_return_list))
        
        # if 'single' parameter is set, only the first item of the list is returned
        if single:
            return return_list[0] if single and return_list else None
        else:
            return return_list


def display_warning(msg):
    print(f"\033[95m\n[WARNING] {msg}\033[0m")
