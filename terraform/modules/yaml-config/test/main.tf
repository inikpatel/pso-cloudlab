module "yaml-file-test" {
  source = "../"

  yaml_config = "./common.yaml"
  json_schema = "./common-schema.json"
}


module "yaml-dir-test" {
  source = "../"

  yaml_config = "./"
  json_schema = "./common-schema.json"
}


output "file-config" {
  value = module.yaml-file-test.config
}

output "dir-config" {
  value = module.yaml-dir-test.config
}
