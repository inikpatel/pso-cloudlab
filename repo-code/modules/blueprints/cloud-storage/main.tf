# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###############################################################################
#                                   Project                                   #
###############################################################################
locals {
  service_encryption_keys = var.service_encryption_keys
}

# module "project" {
#   source          = "../../project"
#   name            = var.project_id
#   parent          = try(var.project_create.parent, null)
#   billing_account = try(var.project_create.billing_account_id, null)
#   project_create  = var.project_create != null
#   prefix          = var.project_create == null ? null : var.prefix
#   services = [
#     "orgpolicy.googleapis.com",
#     "servicenetworking.googleapis.com",
#     "stackdriver.googleapis.com",
#     "storage.googleapis.com",
#     "storage-component.googleapis.com"
#   ]

#   # org_policies = {
#   #   # "compute.requireOsLogin" = {
#   #   #   rules = [{ enforce = false }]
#   #   # }
#   #   # Example of applying a project wide policy, mainly useful for Composer 1
#   # }

#   service_encryption_key_ids = {
#     storage = [try(local.service_encryption_keys.storage, null)]
#   }

#   service_config = {
#     disable_on_destroy = false, disable_dependent_services = false
#   }
# }

###############################################################################
#                              Storage                                        #
###############################################################################

module "bucket" {
  source         = "../../gcs"
  project_id     = var.project_id
  prefix         = var.prefix
  location       = var.location
  name           = "${var.project_id}_data"
  encryption_key = try(local.service_encryption_keys.storage, null) # Example assignment of an encryption key
  force_destroy  = !var.deletion_protection
}
