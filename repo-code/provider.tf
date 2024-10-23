terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      #      version = "~> 4.57"
    }
    google-beta = {
      source = "hashicorp/google-beta"
      #      version = "~> 4.57"
    }
  }
}
provider "google" {
  alias = "impersonation"
  scopes = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
  ]
}

data "google_service_account_access_token" "terraform" {
  provider               = google.impersonation
  target_service_account = var.service_account_email
  scopes                 = ["userinfo-email", "cloud-platform"]
  lifetime               = "1200s"
}

provider "google" {
  access_token    = data.google_service_account_access_token.terraform.access_token
  request_timeout = "60s"
  # comment out to avoid service usage api error
  #  user_project_override = true
}
