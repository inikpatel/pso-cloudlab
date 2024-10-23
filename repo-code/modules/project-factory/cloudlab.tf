# Cloud Lab specific modifications to project factory
# Includes custom group creation and subnet IAM grants

#Service accounts are ouput as:
#   cloud_services = local.service_account_cloud_services
#   default        = local.service_accounts_default
#   robots         = local.service_accounts_robots

# locals {
#   cloud_services = {
#     cloud_services = module.project.service_accounts.cloud_services
#   }
#   all_sa = merge(
#     module.project.service_accounts.robots,
#     module.project.service_accounts.default,
#     local.cloud_services
#   )
# }

# resource "googleworkspace_group" "project_robots_group" {
#   email = "${module.project.name}-robots-group@${var.domain}"
#   name  = "${module.project.name} Cloud Lab Service Agent Group"
# }

# resource "googleworkspace_group_member" "robots_group_member" {
#   for_each = local.all_sa
#   group_id = googleworkspace_group.project_robots_group.id
#   email    = each.value
#   role     = "MEMBER"
# }

# module "group" {
#   source = "terraform-google-modules/group/google"
#   version = "~> 0.6"
#   id = googleworkspace_group.project_robots_group.id
#   members = values(local.all_sa)
# }

# resource "google_compute_subnetwork_iam_member" "robots_group" {
#   for_each   = local.vpc_subnet_bindings
#   project    = local.vpc.host_project
#   subnetwork = "projects/${local.vpc.host_project}/regions/${each.value.region}/subnetworks/${each.value.subnet}"
#   region     = each.value.region
#   role       = "roles/compute.networkUser"
#   member     = "group:${googleworkspace_group.project_robots_group.email}"
#   #member     = "group:${google_cloud_identity_group.project_robots_group.group_key[0].id}"
# }


######## Archive Code Snippets

#Gets group from each subnet binding provided to the project
/*
# data "googleworkspace_group" "project_group" {
#   for_each = local.vpc_subnet_bindings
#   email    = trimprefix(each.value.member, "group:")
# }


#TODO: Create group here instead of through cloud run service to maintain
# Group through TF


# Single gropu memebership block with dynamic sub-block. Ran into issues with duplicate
# members
# resource "googleworkspace_group_members" "robots_group_member" {
#   group_id = googleworkspace_group.project_robots_group.id

#   dynamic "members" {
#     for_each = local.all_sa
#     content {
#       email = members.value
#       role  = "MEMBER"
#     }
#   }
# }

#Cloud Identity instead of workspacce


# resource "google_cloud_identity_group" "project_robots_group" {
#   display_name         = "${module.project.name} Cloud Lab Service Agent Group"
#   initial_group_config = "WITH_INITIAL_OWNER"

#   parent = "customers/${var.customer_id}"

#   group_key {
#     id = "${module.project.name}-robots-group@cloudlab.joonix.net"
#   }

#   labels = {
#     "cloudidentity.googleapis.com/groups.discussion_forum" = ""
#   }
# }


# resource "google_cloud_identity_group_membership" "robots_group_member" {
#   for_each = local.all_sa
#   group    = google_cloud_identity_group.project_robots_group.id

#   preferred_member_key {
#     id = each.value
#   }
#   roles {
#     name = "MEMBER"
#   }
# }

*/
