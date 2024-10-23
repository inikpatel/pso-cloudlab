## Functions
## create project function

module "create-project-function" {
  source                         = "terraform-google-modules/event-function/google"
  version                        = "~> 2.2.0"
  name                           = "create_project_fn"
  description                    = "Reads from firestore, sends to cloud run to create cloud lab project."
  project_id                     = local.project_id
  region                         = var.region
  service_account_email          = google_service_account.cl_function_service_account.email
  available_memory_mb            = 512
  source_directory               = "${path.module}/cloud_functions/create-project/"
  files_to_exclude_in_source_dir = [".zip"]
  runtime                        = "python39"
  entry_point                    = "hello_firestore"
  bucket_name                    = google_storage_bucket.gcf-source.name
  create_bucket                  = false
  max_instances                  = 3000
  event_trigger = {
    event_type = "providers/cloud.firestore/eventTypes/document.create"
    resource   = "projects/${local.project_id}/databases/(default)/documents/collection/{document_wildcard}"
  }
  environment_variables = {
    GIT_FN_URL     = module.git-push-function.uri
    PROJECT_PREFIX = var.prefix
    ENVIRONMENT    = var.environment
    #TOPIC_NAME = google_pubsub_topic.create_project_topic.id,
    #TEMPLATE_FILE = "cloudlab.yaml.template"
    #GIT_URL = module.repo.url,
    #BRANCH = "main"
    #FOLDER_ID = google_folder.cloudlab-projects.name
    QUEUE_NAME = google_cloud_tasks_queue.email_task_queue.id
    #SERVICE_ACCOUNT    = var.service_account_email
    NETWORK_PROJECT    = "deprecate_me"
    NETWORK_REGION     = var.region
    EMAIL_FUNCTION_URL = "deprecate_me"
  }
  depends_on = [
    google_cloud_tasks_queue.email_task_queue
  ]
}

## detach billing function


module "detach-billing-function" {
  source                = "terraform-google-modules/event-function/google"
  version               = "~> 3.0.0"
  project_id            = local.project_id
  region                = var.region
  service_account_email = google_service_account.cl_function_service_account.email
  name                  = "delete_billing_fn"
  description           = "Removes billing account from project when exceeding budget."
  available_memory_mb   = 256
  source_directory      = "${path.module}/cloud_functions/detach-billing/"
  runtime               = "python39"
  entry_point           = "stop_billing"
  bucket_name           = google_storage_bucket.gcf-source.name
  create_bucket         = false
  max_instances         = 3000
  event_trigger = {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.budget_notification_topic.id
  }

  ####TODO####
  #Add pubsub filter to prevent messages that haven't reached threshold from firing function
  #labels                = var.labels
  #service_account_email = var.service_account_email
}

module "increase-budget-function" {
  source           = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-function?ref=v20.0.0"
  v2               = true
  project_id       = local.project_id
  region           = var.region
  service_account  = google_service_account.cl_function_service_account.email
  name             = "increase-budget-http-fn"
  description      = "Increases a projects budget amount."
  bucket_name      = google_storage_bucket.gcf-source.name
  ingress_settings = "ALLOW_ALL"
  function_config = {
    entry_point = "increase_budget"
    runtime     = "python311"
  }
  bundle_config = {
    source_dir  = "${path.module}/cloud_functions/increase-budget/"
    output_path = "${path.module}/cloud_functions/increase-budget/.zip"
    excludes    = [".zip"]
  }
  environment_variables = {
    ORIGIN_URL = module.repo.url
  }
}


module "git-push-function" {
  source           = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-function?ref=v20.0.0"
  v2               = true
  project_id       = local.project_id
  region           = var.region
  service_account  = google_service_account.cl_function_service_account.email
  name             = "git-push-http-fn"
  bucket_name      = google_storage_bucket.gcf-source.name
  ingress_settings = "ALLOW_ALL"
  function_config = {
    entry_point = "create_project"
    runtime     = "python311"
  }
  bundle_config = {
    source_dir  = "${path.module}/cloud_functions/git-push/"
    output_path = "${path.module}/cloud_functions/git-push/.zip"
    excludes    = [".zip"]
  }
  environment_variables = {
    #TOPIC_NAME = google_pubsub_topic.create_project_topic.id
    TEMPLATE_FILE = "cloudlab.yaml.template"
    ORIGIN_URL    = module.repo.url
    #BRANCH = "main"
    FOLDER_ID = google_folder.cloudlab-projects.name
  }
}


/*
module "ui-function" {
  source           = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-function?ref=v20.0.0"
  v2               = true
  project_id       = local.project_id
  region           = var.region
  service_account  = google_service_account.cl_function_service_account.email
  name             = "ui-http-fn"
  bucket_name      = google_storage_bucket.gcf-source.name
  ingress_settings = "ALLOW_ALL"
  function_config = {
    entry_point = "load_html"
    runtime     = "python311"
  }
  bundle_config = {
    source_dir  = "./ui/"
    output_path = "./ui/function.zip"
    excludes    = ["*.zip"]
  }
  environment_variables = {
    GROUP_PREFIX = "deprecate me"
    GROUP_SUFFIX = "deprecate me"
    GROUP_DOMAIN = var.org_domain
    CUSTOMER_ID = var.customer_id
  }
}

*/
