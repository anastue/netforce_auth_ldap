#!/usr/bin/env python3

from setuptools import setup

setup(
    name="netforce_auth_ldap",
    version="3.1.0",
    description="Ldap Module",
    install_requires=[
        "ldap3>=1.4.0",
        "python-ldap",
        "python3-ldap"
    ],

)
