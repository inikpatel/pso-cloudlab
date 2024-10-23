data "external" "yaml_vars" {
  program = ["bash", "-c", "pip3 install pyyaml jsonschema > /dev/null 2>&1 && python3 ${path.module}/files/load-config.py ${var.yaml_config} ${var.json_schema}"]
}

locals {
  yaml_vars = jsondecode(data.external.yaml_vars.result.config)
}
