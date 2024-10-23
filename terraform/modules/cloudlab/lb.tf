/**
 * Copyright 2020 Google LLC
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
  cloud_run_service = "cloud-lab-ui"
}



module "address-fe" {
  source       = "terraform-google-modules/address/google"
  version      = "~> 3.1"
  names        = ["${var.cloudlab_project_name}-ui"]
  global       = true
  region       = var.region
  project_id   = local.project_id
  address_type = "EXTERNAL"
  purpose      = "SHARED_LOADBALANCER_VIP"
}

resource "google_dns_record_set" "cloudlab_dns" {
  count        = var.create_cloud_dns ? 1 : 0
  project      = var.cloud_dns_project
  name         = "${var.ui_fqdn}."
  managed_zone = data.google_dns_managed_zone.cloudlab_dns_zone[0].name
  type         = "A"
  ttl          = 300

  rrdatas = module.address-fe.addresses
}

data "google_dns_managed_zone" "cloudlab_dns_zone" {
  count   = var.create_cloud_dns ? 1 : 0
  project = var.cloud_dns_project
  name    = var.cloud_dns_zone
}


module "lb-http" {
  source  = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  version = "10.0.0"
  name    = local.cloud_run_service
  project = local.project_id

  ssl                             = var.ssl
  managed_ssl_certificate_domains = [var.ui_fqdn]
  https_redirect                  = var.ssl
  create_address                  = false
  address                         = module.address-fe.addresses[0]
  labels = {
    "role"               = "sandbox",
    "target-environment" = var.environment,
    "hosting"            = "cloudlab-projects",
    "creator"            = "cloudlab"
  }

  backends = {
    default = {
      description             = null
      protocol                = "HTTP"
      port_name               = null
      enable_cdn              = false
      custom_request_headers  = null
      custom_response_headers = null
      security_policy         = null
      compression_mode        = null

      log_config = {
        enable      = true
        sample_rate = 1.0
      }

      groups = [
        {
          group = google_compute_region_network_endpoint_group.serverless_neg.id
        }
      ]

      iap_config = try({
        enable               = var.enable_iap
        oauth2_client_id     = google_iap_client.iap_client.client_id
        oauth2_client_secret = google_iap_client.iap_client.secret
      }, null)
    }
  }
}

resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  provider              = google-beta
  name                  = "serverless-neg"
  network_endpoint_type = "SERVERLESS"
  project               = local.project_id
  region                = var.region
  cloud_run {
    service = local.cloud_run_service
  }
}

/*  IAP terraform manged for future state. Has restrictions on UI usage

resource "google_iap_brand" "iap_brand" {
  support_email     = var.iap_support_email
  application_title = "CloudLab IAP protected Application"
  project           = google_project_service.project_service.project
}

resource "google_iap_client" "iap_client" {
  display_name = "CloudLab IAP Client"
  brand        =  google_iap_brand.project_brand.name
}

*/
# /*
# resource "google_project" "project" {
#   project_id = var.project_id
#   name       = var.project_name
#   org_id     = var.org_id
# }
# */

resource "google_project_service_identity" "iap_sa" {
  provider = google-beta
  project  = local.project_id
  service  = "iap.googleapis.com"
}

resource "google_project_iam_member" "cloudlab_iap_sa" {
  project = local.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_project_service_identity.iap_sa.email}"
}

resource "google_project_service" "project_service" {
  project = local.project_id
  service = "iap.googleapis.com"
}

resource "google_iap_brand" "project_brand" {
  support_email     = var.iap_support_email
  application_title = "Cloud Lab"
  project           = google_project_service.project_service.project
}

resource "google_iap_client" "iap_client" {
  display_name = "IAP-cloud-lab-ui-backend-default"
  brand        = google_iap_brand.project_brand.name
}
