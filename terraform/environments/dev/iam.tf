resource "google_project_iam_member" "cloub_lab_web_app_users" {
  project = module.cloudlab-inf.cloudlab_project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "group:gcp-cloudlab-web-app-users@example.com"
}
