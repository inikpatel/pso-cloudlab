variable "cloudlab_project_id" {
  description = "Project ID of an existing project to use for cloudlab infra"
  type        = string
  default     = null
}

variable "cloudlab_project_name" {
  description = "Cloud Lab Builder Project name (not project_id or number)"
  type        = string
  default     = "cloudlab-infra"
}

variable "region" {
  description = "GCP Region location"
  type        = string
}

variable "org_id" {
  description = "GCP Org ID"
  type        = string
}

variable "folder_id" {
  description = "Folder in Org to create Cloud Lab"
  type        = string
}

variable "prefix" {
  description = "Prefix for Cloud Lab Resources"
  type        = string
}

variable "environment" {
  description = "Environment prefix for Cloud Lab Resources"
  type        = string
  default     = "dev"
}

variable "billing_account" {
  description = "GCP Billing Account"
  type        = string
}

variable "group_org_admins" {
  description = "Admin Group"
  type        = string
}

variable "group_billing_admins" {
  description = "Billing Admin Group"
  type        = string
}

variable "terraform_sa_name" {
  description = "Cloud Lab Terraform Service Account"
  type        = string
  default     = "cloudlab-terraform"
}

variable "identity_service_account" {
  description = "Cloud Lab UI Identity Service Account"
  type        = string
  default     = "cloudlab-ui-identity"
}

variable "service_account_email" {
  description = "Service account to use for gcp resources"
  type        = string
  default     = null
}

variable "service_account_project_id" {
  description = "Project that the external service account lives in. The service account/user deploying code must have appropriate permissions"
  type        = string
  default     = null
}

variable "iap_oauth_client" {
  description = "Identity Aware Proxy oauth Client ID"
  type        = string
  default     = null
}

variable "iap_oauth_secret" {
  description = "Identity Aware Proxy oauth Client Secret"
  default     = null
  type        = string
}

variable "iap_support_email" {
  description = "Identity Aware Proxy support email"
  type        = string
  default     = null
}

variable "enable_iap" {
  description = "Enable Identity Aware Proxy"
  type        = string
  default     = "false"
}

variable "org_domain" {
  description = "GCP and Workspace domain name"
  type        = string
}

variable "ui_fqdn" {
  description = "Domain name to run the HTTPS load balancer on"
  type        = string
}


variable "ssl" {
  description = "Provision managed SSL certificate for the HTTPS Load Balancer"
  type        = bool
  default     = true

}

variable "ssl_certificates" {
  description = "SSL certificates used by the HTTP load balaner."
  type        = list(string)
  default     = []
}

variable "reserved_external_ip" {
  description = "External global IPv4 address that has already been reserved."
  type        = string
  default     = null
}

variable "is_goog_internal" {
  description = "Boolean field used to enable for Google PSO internal testing."
  type        = bool
  default     = false
}

variable "group_prefix" {
  description = "Optional suffix to append to group creation."
  type        = string
  default     = null
}

variable "group_suffix" {
  description = "Optional suffix to append to group creation."
  type        = string
  default     = null
}

variable "host_project" {
  description = "Optional project ID for the shared VPC host project."
  type        = string
  default     = null
}

variable "customer_id" {
  description = "Google Workspace Customer ID for group management."
  type        = string
  default     = null
}

variable "email_sender" {
  description = "No-reply email address to send emails from. Must match org_domain."
  type        = string
  default     = null
}

variable "create_cloud_dns" {
  description = "Controls if a Cloud DNS entry is created. If not, DNS must be updated manually"
  type        = bool
  default     = false

}

variable "cloud_dns_zone" {
  description = "Managed zone name for Cloud DNS."
  type        = string
  default     = null

}

variable "cloud_dns_project" {
  description = "Managed zone GCP Project ID."
  type        = string
  default     = null

}
