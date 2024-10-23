/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */



locals {
  _defaults = yamldecode(file(var.defaults_file))
  _defaults_net = {
    #billing_account_id   = var.billing_account.id
    #environment_dns_zone = var.environment_dns_zone
    shared_vpc_self_link = try(var.vpc_self_links["cloudlab-net-example"], null)
    vpc_host_project     = try(var.host_project_ids["cloudlab-net-example"], null)
  }

  defaults = merge(local._defaults, local._defaults_net)

  projects = {
    for f in fileset("${var.data_dir}", "**/*.yaml") :
    trimsuffix(f, ".yaml") => yamldecode(file("${var.data_dir}/${f}"))
  }

  default_projects = {
    for k, v in local.projects :
    k => v if lookup(v, "template", "default") == "default"
  }

  playground_projects = {
    for k, v in local.projects :
    k => v if lookup(v, "template", "default") == "data-playground"
  }

  cloud_storage = {
    for k, v in local.projects :
    k => v if lookup(v, "template", "default") == "cloud-storage"
  }

}

#  projects are created for all cloud lab instances
module "projects" {
  source             = "./modules/project-factory"
  for_each           = local.projects
  defaults           = local.defaults
  project_id         = each.key
  billing_account_id = try(each.value.billing_account_id, null)
  billing_alert      = try(each.value.billing_alert, null)
  dns_zones          = try(each.value.dns_zones, [])
  essential_contacts = try(each.value.essential_contacts, [])
  #todo: add folder to defaults
  #another comment
  folder_id = each.value.folder_id
  group_iam = try(each.value.group_iam, {})
  # iam                    = {
  #   "roles/resourcemanager.projectIamAdmin": [
  #       replace(replace("user:${each.value.labels.requestor}", "__", "@"), "_", ".")
  #   ]
  # }
  iam                    = try(each.value.iam, {})
  kms_service_agents     = try(each.value.kms, {})
  labels                 = try(each.value.labels, {})
  org_policies           = try(each.value.org_policies, null)
  service_accounts       = try(each.value.service_accounts, {})
  service_accounts_iam   = try(each.value.service_accounts_iam, {})
  services               = try(each.value.services, [])
  service_identities_iam = try(each.value.service_identities_iam, {})
  vpc                    = try(each.value.vpc, null)
  domain                 = var.customer_domain
  #prefix                 = var.prefix
}

# add data playground blueprint for data_playground projects
module "data_playground" {
  source = "./modules/blueprints/data-playground"

  for_each = local.playground_projects

  project_create = null # do not create new project

  project_id = module.projects[each.key].project_id
  prefix     = "dp"

}

# add cloud storage blueprint for cloud-storage projects
module "cloud_storage" {
  source = "./modules/blueprints/cloud-storage"

  for_each = local.cloud_storage

  project_create = null # do not create new project

  project_id = module.projects[each.key].project_id

  prefix = "gcs"

}
