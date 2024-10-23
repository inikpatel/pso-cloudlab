
locals {
  activate_apis = [
    "serviceusage.googleapis.com",
    "admin.googleapis.com",
    "appengine.googleapis.com",
    "appenginereporting.googleapis.com",
    "artifactregistry.googleapis.com",
    "billingbudgets.googleapis.com",
    "certificatemanager.googleapis.com",
    "cloudapis.googleapis.com",
    "cloudasset.googleapis.com",
    "cloudbilling.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudidentity.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtasks.googleapis.com",
    "compute.googleapis.com",
    "containerregistry.googleapis.com",
    "datastore.googleapis.com",
    "dns.googleapis.com",
    "essentialcontacts.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "iap.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "sourcerepo.googleapis.com",
    "storage.googleapis.com",
  ]

  project_id            = var.cloudlab_project_id != null ? module.project-services[0].project_id : module.project[0].project_id
  service_account_project_id = try(var.service_account_project_id, local.project_id)
  service_account = var.service_account_email!=null ? "projects/${local.service_account_project_id}/serviceAccounts/${var.service_account_email}" : resource.google_service_account.cl_tf_service_account.id
  #old config cloudlab_project_folder = "folders/${var.folder_id}"
}

###Project###

module "project" {
  count   = var.cloudlab_project_id != null ? 0 : 1
  source  = "terraform-google-modules/project-factory/google"
  version = "~> 14.4.0"

  name            = "${var.prefix}-${var.cloudlab_project_name}-${var.environment}"
  project_id      = "${var.prefix}-${var.cloudlab_project_name}-${var.environment}-${random_id.proj_id.hex}"
  org_id          = var.org_id
  folder_id       = var.folder_id
  billing_account = var.billing_account
  #default_service_account = "keep"
  activate_apis               = local.activate_apis
  disable_services_on_destroy = true
  sa_role                     = "roles/editor"

}

# add random project id
resource "random_id" "proj_id" {
  byte_length = 2
}


resource "google_project_service" "beta_iap" {
  provider           = google-beta
  project            = local.project_id
  service            = "iap.googleapis.com"
  disable_on_destroy = true
}


module "project-services" {
  count                       = var.cloudlab_project_id != null ? 1 : 0
  source                      = "terraform-google-modules/project-factory/google//modules/project_services"
  version                     = "~> 14.2"
  project_id                  = var.cloudlab_project_id != null ? var.cloudlab_project_id : module.project[0].project_id
  activate_apis               = local.activate_apis
  disable_services_on_destroy = false
}


resource "google_folder" "cloudlab-projects" {
  display_name = "Cloudlab User Projects - ${var.environment}"
  parent       = "folders/${var.folder_id}"

}

##GCS Buckets##

resource "google_storage_bucket" "tfstate" {
  name                        = "${var.prefix}-${local.project_id}-tfstate-${var.environment}"
  location                    = var.region
  project                     = local.project_id
  uniform_bucket_level_access = true
  #change force_destroy to false when ready for production use
  force_destroy = true
}

resource "google_storage_bucket" "gcf-source" {
  name                        = "${var.prefix}-${local.project_id}-gcf-tf-source-${var.environment}"
  location                    = var.region
  project                     = local.project_id
  uniform_bucket_level_access = true
  #change force_destroy to false when ready for production use
  force_destroy = true
}


##PubSub##

resource "google_pubsub_topic" "create_project_topic" {
  name    = "${var.prefix}-cloudlab-create-prj-topic-${var.environment}"
  project = local.project_id
}

resource "google_pubsub_topic" "increase_budget_topic" {
  name    = "${var.prefix}-cloudlab-increase-budget-topic-${var.environment}"
  project = local.project_id
}

resource "google_pubsub_topic" "budget_notification_topic" {
  name    = "${var.prefix}-cloudlab-budget-notificaiton-topic-${var.environment}"
  project = local.project_id
}

## Firestore

resource "google_firestore_database" "firestore" {
  project                 = local.project_id
  name                    = "(default)"
  location_id             = var.region
  type                    = "FIRESTORE_NATIVE"
  delete_protection_state = "DELETE_PROTECTION_ENABLED"
}

resource "google_firestore_document" "schema" {
  project     = local.project_id
  collection  = "collection"
  document_id = "schema"
  fields      = "{\"description\":{\"stringValue\":\"Example\"}, \"user_email\":{\"stringValue\":\"example@domain.com\"}, \"project_name\":{\"stringValue\":\"XYZ\"}, \"project_state\":{\"stringValue\":\"submitted\"}, \"terms_accepted\":{\"stringValue\":\"y\"}, \"terms_accept_time\":{\"integerValue\":\"0\"}, \"data_type\":{\"stringValue\":\"academic\"},  \"group_email\":{\"stringValue\":\"group@example.com\"}}"
  depends_on  = [google_firestore_database.firestore]
}


#Source Repo

module "repo" {
  source     = "../source-repository"
  project_id = local.project_id
  region     = var.region
  name       = "cloudlab-repo"
  triggers = {
    cloudlab-projects = {
      filename       = ".cloudbuild/cloudbuild-workflow.yaml"
      included_files = ["**/*tf", "**/*.yaml"]
      # use local project service account, impersonation setting in provider.tf
      service_account = local.service_account
      substitutions = {
        _CL_BILLING_ACCOUNT = "{id = ${var.billing_account} organization_id = ${var.org_id}}"
        _CL_FOLDER          = var.folder_id
        _CUSTOMER_ID        = var.customer_id
        _CUSTOMER_DOMAIN    = var.org_domain
        _PREFIX             = "projects/state"
        _TF_STATE_BUCKET    = google_storage_bucket.tfstate.name
        _TF_VERSION         = "1.7.4"
      }
      template = {
        branch_name = "main"
        project_id  = null
        tag_name    = null
      }
    }
  }
}


# cloud task queue
resource "google_cloud_tasks_queue" "email_task_queue" {
  name     = "email-tasks-queue"
  location = var.region
  project  = local.project_id
  stackdriver_logging_config {
    sampling_ratio = 1
  }
}
