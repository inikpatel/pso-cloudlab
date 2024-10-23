# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Usage:
# python scripts/load-config.py <config.yaml> [<schema.json>]

"""
Program name: load-config.py

  Load configuration from a YAML file and validated with JSON schema

Descript:
  This Python script is used by Terraform external data source to load configuration file
  from an external YAML file, and validate against a JSON schema file.

  Input:
  - configuration YAML file, for example:
      billing_account: ABCD-EFGH
      org_id: 12345678
    OR
    configuration YAML file folder with the same type of files

  - JSON schema file, for example:
    {
      "type": "object",
      "properties": {
        "billing_account": {"type": "string"},
        "org_id": {"type": "number"},
        "bootstrap_user": {"type": "string"},
        "project_id": {"type": "string"},
        "default_region": {"type": "string"}
      },
      "required": ["billing_account", "org_id"]
    }

  Output:
    {"config": "{\"org_id\": 12345678, \"billing_account\": \"ABCD-EFGH\"}"}
  OR
    {"config: "[{\"org_id\": 12345678, \"billing_account\": \"ABCD-EFGH\"}]"}


  Usage:

    Inside Terraform script, we can define an external data source then reference it:

    data "external" "yaml_common_vars" {
      program = ["python", "scripts/load-config.py", "../config/common-vars.yaml", "../config/schema/common-schema.json" ]
    }

    locals {
      common_vars = jsondecode(data.external.yaml_common_vars.result.config)
      billing_account = local.common_vars.billing_account
    }

  Test:
    python load-config.py ../test/common.yaml ../../test/schema/common-schema.json

"""
#!/bin/python

import yaml
import json
import jsonschema
import sys
import os

###
# Function: validate_json()
###

def validate_json(data, schema):
  """
  Function: validate JSON schema

  Input:
  - data: JSON object
  - schema: JSON schema dictionary

  Output:
  - Success: True
  - Failure: False with print out
  """
  try:
    jsonschema.validate(instance=data, schema=schema)
    return True
  except jsonschema.exceptions.ValidationError as ve:
    print(f"Validation error: {ve}")
    return False

###
# Function: read_yaml_file()
###

def read_yaml_file(file_path):
  """
  Function: read YAML file

  Input:
  - file_path: path of the YAML file

  Output:
  - Python Object
  """
  try:
    with open(file_path, 'r') as yfile:
      data = yaml.safe_load(yfile)
      return data
  except Exception as e:
    print(f"Error reading configuration file: {e}", file=sys.stderr)
    sys.exit(1)

###
# Function: load_json_schema()
###

def load_json_schema(file_path):
  """
  Function: Load JSON Schema file

  Input:
  - file_path: JSON schema file path

  Output:
  - JSON string
  """
  try:
    with open(file_path, "r") as sfile:
      return json.load(sfile)
  except Exception as e:
    print(f"Error reading schema file: {e}", file=sys.stderr)
    sys.exit(1)


###
# Function: parse_yaml_file
###
def process_yaml_file(config_path, schema_path=""):
  """
  Process a single YAML file and validate against JSON schema

  Input:
  - config_path: YAML configuration file
  - schema_path: JSON schema file, optional, default is ""

  Output:
  - Python dictionary of YAML data
  """

  # load file
  yaml_data = read_yaml_file(config_path)

  # convert to a JSON string then JSON object
  cfg_json = json.loads(json.dumps(yaml_data))

  # validate against schema if provided
  if schema_path != "":
    schema  = load_json_schema(schema_path)

    if not validate_json(cfg_json, schema):
      sys.exit(1)

  return yaml_data



#----------------------------------------------------------------
# Main function
#----------------------------------------------------------------
def main():
  """
  Helper function to load YAML configuration and optionally validate
  it against a JSON schema file.

  Input:
  - YAML file path or directory path
  - JSON schema file path (optional), if not provided then no schema check

  Output:
  JSON string of the configuration data to be consumed by Terraform
  external data source module
  """

  schema_path = ""

  if len(sys.argv) == 3:
    schema_path = sys.argv[2]
  elif len(sys.argv) != 2:
    print(f"Usage: python load-config.py <path_to_config_file> [<path_to_schema_file>]", file=sys.stderr)
    sys.exit(1)

  # load configuration YAML file
  config_path = sys.argv[1]

  json_str = ""

  if os.path.isfile(config_path):
    yaml_data = process_yaml_file(config_path, schema_path)
    json_str = json.dumps(yaml_data)
  elif os.path.isdir(config_path):
    json_list = []
    for fname in os.listdir(config_path):
      if fname.endswith('.yaml'):
        fpath = os.path.join(config_path, fname)
        yaml_data = process_yaml_file(fpath, schema_path)
        json_list.append(yaml_data)
    json_str = json.dumps(json_list)
  else:
    print("Error: invalid YAML config path.")
    sys.exit(1)

  # return configuration data as JSON encoded value of 'config'
  print(json.dumps({"config": json_str}))

if __name__ == "__main__":
  main()
