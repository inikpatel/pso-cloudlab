/***********************************************
 CloudLab - Cloud Run Image
 ***********************************************/

locals {
  ts_tag = formatdate("YYYYMMDD.HHmmss", timestamp())
}

# data "archive_file" "cloudrun_ui" {
#   type        = "zip"
#   output_path = "${path.module}/ui/.zip"
#   source_dir  = "${path.module}/ui"
# }

# use artifact registry to store the image, since container registry is sunsetting
resource "google_artifact_registry_repository" "cloud_lab_ui_repository" {
  location      = var.region
  repository_id = "cloudlab-ui"
  description   = "CloudLab UI repository"
  project       = local.project_id
  format        = "docker"
}

# grant access to the repository
# resource "google_artifact_registry_repository_iam_member" "repo_reader" {
#   provider = google-beta
#   location = google_artifact_registry_repository.cloud_lab_ui_repository.location
#   repository = google_artifact_registry_repository.cloud_lab_ui_repository.name
#   role = "roles/artifactregistry.reader"
#   member = "serviceAccount:${var.service_account_email}"
#   project = local.project_id
# }

# resource "google_project_iam_member" "artifact_registry_writer"  {
#   project = local.project_id
#   member = "serviceAccount:${var.service_account_email}"
#   role = "roles/artifactregistry.writer"
# }

resource "null_resource" "cloudlab_ui_image_builder" {
  triggers = {
    project_id_cloudbuild_project = local.project_id
    gar_location                  = var.region
    #    md5                           = data.archive_file.cloudrun_ui.output_md5
    code_hash = join(",", [
      for file in fileset("${path.module}/ui/", "**") : filesha256("${path.module}/ui/${file}")
    ])
  }

  provisioner "local-exec" {
    command = <<EOT
      gcloud builds submit ${path.module}/ui/ --project ${local.project_id} --gcs-source-staging-dir=gs://${var.prefix}-${local.project_id}_cloudbuild/source --tag ${var.region}-docker.pkg.dev/${local.project_id}/cloudlab-ui/cloud_lab_ui:${local.ts_tag} --tag ${var.region}-docker.pkg.dev/${local.project_id}/cloudlab-ui/cloud_lab_ui:latest --impersonate-service-account=${var.service_account_email}
      EOT
  }

}

/***********************************************
 CloudLab - Cloud Run
 ***********************************************/

module "cloud_lab_ui" {
  source     = "GoogleCloudPlatform/cloud-run/google"
  version    = "~> 0.2.0"
  depends_on = [null_resource.cloudlab_ui_image_builder]
  # Required variables
  service_name = "cloud-lab-ui"
  project_id   = local.project_id
  location     = var.region
  # image                 = "us.gcr.io/${local.project_id}/cloud_lab_ui:latest"
  image                 = "${var.region}-docker.pkg.dev/${local.project_id}/cloudlab-ui/cloud_lab_ui:latest"
  service_account_email = google_service_account.cl_cloudrun_service_account.email
  container_concurrency = 80
  limits = {
    "cpu"    = "1000m"
    "memory" = "512Mi"
  }
  #allUsers required for use with IAP. Service annotation prevents public access
  members = ["allUsers"]
  service_annotations = {
    "run.googleapis.com/ingress" : "internal-and-cloud-load-balancing"
  }
  #satisfiesPzs = true is applied by default, capturing here to avoid plan changes
  service_labels = {
    "run.googleapis.com/satisfiesPzs" = true
  }
  env_vars = [
    {
      name  = "GROUP_PREFIX"
      value = var.group_prefix
    },
    {
      name  = "GROUP_SUFFIX"
      value = var.group_suffix
    },
    {
      name  = "GROUP_DOMAIN"
      value = var.org_domain
    },
    {
      name  = "CUSTOMER_ID"
      value = var.customer_id
    },
    {
      name  = "IAP_AUD"
      value = try(nonsensitive(module.lb-http.backend_services.default.generated_id), "")
    }
  ]
}
