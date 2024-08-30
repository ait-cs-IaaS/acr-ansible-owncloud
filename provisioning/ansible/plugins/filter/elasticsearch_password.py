#!/usr/bin/env python3
from ansible.errors import AnsibleFilterError
from passlib.hash import bcrypt


class FilterModule(object):

    def filters(self):
        return {
            "elasticsearch_password" : FilterModule.encrypt_elasticseach_password
        }

    @staticmethod
    def encrypt_elasticseach_password(password: str):
        if not isinstance(password, str):
            raise AnsibleFilterError("Input needs to be string but got:'{password}' with type:'{type(password)}'")
        return bcrypt.using(ident="2a", rounds=10).hash(password)

