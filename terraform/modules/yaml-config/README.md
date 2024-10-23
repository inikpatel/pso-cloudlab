# YAML configuration module

This module takes two parameters:

- YAML configuration file or a folder contains multiple YAML configuration files in the same type
- JSON schema file (optional)

and return data `config` to be used by other Terraform steps.

It can be used to complement the regular Terraform variable files and make it
easy for users to load more user friendly YAML configuration files with schema
check.
