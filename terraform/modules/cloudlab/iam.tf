/***********************************************
  Cloud Lab IAM
 ***********************************************/

/***********************************************
  Data Resources
 ***********************************************/
/*
data "google_compute_default_service_account" "default" {
  project = local.project_id
}

data "google_app_engine_default_service_account" "default" {
  project = local.project_id
}
*/

# The usage below is intended for the use case of cloud build needing to impersonate an
# account that lives in a different project

data "google_service_account" "cl_tf_service_account" {
  account_id = var.service_account_email != null ? var.service_account_email : resource.google_service_account.cl_tf_service_account.email
  project    = var.service_account_email != null ? var.service_account_project_id : local.project_id
}

# data "google_organization" "gcp_org" {
#   domain = var.org_domain
# }

data "google_project" "cloudlab_project_data" {
  project_id = local.project_id
  depends_on = [
    module.project
  ]
}


/***********************************************
  Service Accounts
 ***********************************************/

resource "google_service_account" "cl_tf_service_account" {
  account_id   = "cloudlab-terraform-sa"
  display_name = "Cloud Lab Terraform Service Account"
  project      = local.project_id
}

resource "google_service_account" "cl_function_service_account" {
  account_id   = "cloudlab-function-sa"
  display_name = "Cloud Lab Cloud Functions Service Account"
  project      = local.project_id
}

resource "google_service_account" "cl_cloudrun_service_account" {
  account_id   = "cloudlab-cloudrun-sa"
  display_name = "Cloud Lab Cloud Run Service Account"
  project      = local.project_id
}

/***********************************************
  IAM Grants
 ***********************************************/

/***********************************************
  START OPTIONAL GRANTS
 ***********************************************/

#Compute needs billing user and cost management
#Don't apply IAM for billing for google internal due to corp policies.

# resource "google_billing_account_iam_member" "user" {
#   count              = var.is_goog_internal == true ? 0 : 1
#   billing_account_id = var.billing_account
#   role               = "roles/billing.user"
#   member             = resource.google_service_account.cl_tf_service_account.member
# }

# resource "google_billing_account_iam_member" "cost_admin" {
#   count              = var.is_goog_internal == true ? 0 : 1
#   billing_account_id = var.billing_account
#   role               = "roles/billing.costsManager"
#   member             = resource.google_service_account.cl_tf_service_account.member
# }


resource "google_service_account_iam_member" "org-build-agent" {
  count              = var.service_account_email != null ? 1 : 0
  service_account_id = data.google_service_account.cl_tf_service_account.id
  role               = "roles/cloudbuild.serviceAgent"
  member             = "serviceAccount:service-${data.google_project.cloudlab_project_data.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "org-build-impersonate" {
  count              = var.service_account_email != null ? 1 : 0
  service_account_id = data.google_service_account.cl_tf_service_account.id
  role               = "roles/iam.serviceAccountUser"
  member             = resource.google_service_account.cl_tf_service_account.member
}

resource "google_service_account_iam_member" "org-build-agent-impersonate" {
  count              = var.service_account_email != null ? 1 : 0
  service_account_id = data.google_service_account.cl_tf_service_account.id
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:service-${data.google_project.cloudlab_project_data.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "org-build-token" {
  count              = var.service_account_email != null ? 1 : 0
  service_account_id = data.google_service_account.cl_tf_service_account.id
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = resource.google_service_account.cl_tf_service_account.member
}

/***********************************************
  END OPTIONAL GRANTS
 ***********************************************/

#Compute needs folder admin/project creator

resource "google_folder_iam_member" "folder" {
  folder = google_folder.cloudlab-projects.name
  role   = "roles/resourcemanager.projectCreator"
  member = data.google_service_account.cl_tf_service_account.member
}
#cloud function service account needs resource get on folder
#resource "google_folder_iam_member" "folder_viewer" {
#  folder = local.cloudlab_project_folder
#  role   = "roles/browser"
#  member = "serviceAccount:${var.service_account_email}"
#}
resource "google_folder_iam_member" "tf_folder_admin" {
  folder = google_folder.cloudlab-projects.name
  role   = "roles/resourcemanager.folderAdmin"
  member = data.google_service_account.cl_tf_service_account.member
}

resource "google_folder_iam_member" "fn_folder_viewer" {
  folder = google_folder.cloudlab-projects.name
  role   = "roles/resourcemanager.folderViewer"
  member = resource.google_service_account.cl_function_service_account.member
}

resource "google_folder_iam_member" "cloudrun_folder_viewer" {
  folder = google_folder.cloudlab-projects.name
  role   = "roles/resourcemanager.folderViewer"
  member = resource.google_service_account.cl_cloudrun_service_account.member
}

resource "google_folder_iam_member" "owner" {
  folder = "folders/${var.folder_id}"
  role   = "roles/owner"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "pubsub_admin" {
  project = local.project_id
  role    = "roles/pubsub.admin"
  member  = resource.google_service_account.cl_tf_service_account.member
}

resource "google_project_iam_member" "datastore_user_tf" {
  project = local.project_id
  role    = "roles/datastore.user"
  member  = data.google_service_account.cl_tf_service_account.member
}

resource "google_project_iam_member" "datastore_user_cloudfunction" {
  project = local.project_id
  role    = "roles/datastore.user"
  member  = resource.google_service_account.cl_function_service_account.member
}

resource "google_project_iam_member" "datastore_user_cloudrun" {
  project = local.project_id
  role    = "roles/datastore.user"
  member  = resource.google_service_account.cl_cloudrun_service_account.member
}

resource "google_project_iam_member" "function_invoker" {
  project = local.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = resource.google_service_account.cl_function_service_account.member
}

resource "google_project_iam_member" "cloudrun_invoker" {
  project = local.project_id
  role    = "roles/run.invoker"
  member  = resource.google_service_account.cl_function_service_account.member
}

resource "google_project_iam_member" "cloudtasks_enqueuer" {
  project = local.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = resource.google_service_account.cl_function_service_account.member
}

resource "google_service_account_iam_member" "tasks_function_user" {
  service_account_id = resource.google_service_account.cl_function_service_account.name
  role               = "roles/iam.serviceAccountUser"
  member             = resource.google_service_account.cl_function_service_account.member
}

resource "google_project_iam_member" "sourcerepo_writer" {
  project = local.project_id
  role    = "roles/source.writer"
  member  = resource.google_service_account.cl_function_service_account.member
}

resource "google_project_iam_member" "cloudbuild_builder_data_tf" {
  project = local.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = data.google_service_account.cl_tf_service_account.member
}

resource "google_project_iam_member" "cloudbuild_builder_tf" {
  project = local.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = resource.google_service_account.cl_tf_service_account.member
}

resource "google_project_iam_member" "iap_domain_users" {
  project = local.project_id
  role    = "roles/iap.httpsResourceAccessor"
  # member  = "domain:${data.google_organization.gcp_org.domain}"
  member = "domain:${var.org_domain}"
}

#For shared VPC attachment. Can be trimmed down with a custom role
resource "google_project_iam_member" "subnet_viewer" {
  project = var.host_project != null ? var.host_project : local.project_id
  role    = "roles/compute.viewer"
  member  = resource.google_service_account.cl_function_service_account.member
}
