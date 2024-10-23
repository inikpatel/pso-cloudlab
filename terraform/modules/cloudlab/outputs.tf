output "cloudlab_endpoint" {
  value       = module.lb-http.external_ip
  description = "IP Address that serves the CloudLab UI"
}

output "cloudlab_project_id" {
  value       = local.project_id
  description = "Cloudlab Infrastructure Project ID"
}

output "cloudlab_folder_id" {
  value       = google_folder.cloudlab-projects.folder_id
  description = "Folder created for end user projects"

}

output "cloudlab_budget_pubsub" {
  value       = google_pubsub_topic.budget_notification_topic.id
  description = "Cloudlab Budget Notification Pubsub Topic"
}

output "cloudlab_ar_repo" {
  value       = google_artifact_registry_repository.cloud_lab_ui_repository.id
  description = "Cloudlab Artifact Registry Repository"
}
