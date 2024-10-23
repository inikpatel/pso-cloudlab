/**
 * Copyright 2024 Google LLC
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
  cfg = yamldecode(file("./config/cloudlab.yaml"))
}

module "cloudlab-inf" {
  source = "../../modules/cloudlab"

  cloudlab_project_name = local.cfg.cloudlab_project_name
  cloudlab_project_id   = try(local.cfg.cloudlab_project_id, null)

  prefix                     = local.cfg.prefix
  region                     = local.cfg.region
  org_id                     = local.cfg.org_id
  folder_id                  = local.cfg.folder_id
  billing_account            = local.cfg.billing_account
  group_org_admins           = local.cfg.group_org_admins
  group_billing_admins       = local.cfg.group_billing_admins
  service_account_email      = try(local.cfg.service_account_email, null)
  service_account_project_id = try(local.cfg.service_account_project_id, null)
  identity_service_account   = local.cfg.identity_service_account
  environment                = local.cfg.environment
  org_domain                 = local.cfg.org_domain
  ssl_certificates           = try(local.cfg.ssl_certificates, null)
  enable_iap                 = local.cfg.enable_iap
  iap_support_email          = try(local.cfg.iap_support_email, "")
  ui_fqdn                    = try(local.cfg.ui_fqdn, null)
  iap_oauth_client           = try(local.cfg.iap_oauth_client, null)
  iap_oauth_secret           = try(local.cfg.iap_oauth_secret, null)

}