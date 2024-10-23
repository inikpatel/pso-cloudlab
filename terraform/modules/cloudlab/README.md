<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_google"></a> [google](#provider\_google) | n/a |
| <a name="provider_google-beta"></a> [google-beta](#provider\_google-beta) | n/a |
| <a name="provider_null"></a> [null](#provider\_null) | n/a |
| <a name="provider_random"></a> [random](#provider\_random) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_address-fe"></a> [address-fe](#module\_address-fe) | terraform-google-modules/address/google | ~> 3.1 |
| <a name="module_cloud_lab_ui"></a> [cloud\_lab\_ui](#module\_cloud\_lab\_ui) | GoogleCloudPlatform/cloud-run/google | ~> 0.2.0 |
| <a name="module_create-project-function"></a> [create-project-function](#module\_create-project-function) | terraform-google-modules/event-function/google | ~> 2.2.0 |
| <a name="module_detach-billing-function"></a> [detach-billing-function](#module\_detach-billing-function) | terraform-google-modules/event-function/google | ~> 3.0.0 |
| <a name="module_git-push-function"></a> [git-push-function](#module\_git-push-function) | github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-function | v20.0.0 |
| <a name="module_increase-budget-function"></a> [increase-budget-function](#module\_increase-budget-function) | github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-function | v20.0.0 |
| <a name="module_lb-http"></a> [lb-http](#module\_lb-http) | GoogleCloudPlatform/lb-http/google//modules/serverless_negs | 10.0.0 |
| <a name="module_project"></a> [project](#module\_project) | terraform-google-modules/project-factory/google | ~> 14.4.0 |
| <a name="module_project-services"></a> [project-services](#module\_project-services) | terraform-google-modules/project-factory/google//modules/project_services | ~> 14.2 |
| <a name="module_repo"></a> [repo](#module\_repo) | ../source-repository | n/a |

## Resources

| Name | Type |
|------|------|
| [google-beta_google_compute_region_network_endpoint_group.serverless_neg](https://registry.terraform.io/providers/hashicorp/google-beta/latest/docs/resources/google_compute_region_network_endpoint_group) | resource |
| [google-beta_google_project_service.beta_iap](https://registry.terraform.io/providers/hashicorp/google-beta/latest/docs/resources/google_project_service) | resource |
| [google-beta_google_project_service_identity.iap_sa](https://registry.terraform.io/providers/hashicorp/google-beta/latest/docs/resources/google_project_service_identity) | resource |
| [google_artifact_registry_repository.cloud_lab_ui_repository](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/artifact_registry_repository) | resource |
| [google_cloud_tasks_queue.email_task_queue](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_tasks_queue) | resource |
| [google_dns_record_set.cloudlab_dns](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dns_record_set) | resource |
| [google_firestore_database.firestore](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/firestore_database) | resource |
| [google_firestore_document.schema](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/firestore_document) | resource |
| [google_folder.cloudlab-projects](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder) | resource |
| [google_folder_iam_member.cloudrun_folder_viewer](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder_iam_member) | resource |
| [google_folder_iam_member.fn_folder_viewer](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder_iam_member) | resource |
| [google_folder_iam_member.folder](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder_iam_member) | resource |
| [google_folder_iam_member.owner](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder_iam_member) | resource |
| [google_folder_iam_member.tf_folder_admin](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/folder_iam_member) | resource |
| [google_iap_brand.project_brand](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iap_brand) | resource |
| [google_iap_client.iap_client](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iap_client) | resource |
| [google_project_iam_member.cloudbuild_builder_data_tf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.cloudbuild_builder_tf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.cloudlab_iap_sa](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.cloudrun_invoker](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.cloudtasks_enqueuer](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.datastore_user_cloudfunction](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.datastore_user_cloudrun](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.datastore_user_tf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.function_invoker](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.iap_domain_users](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.pubsub_admin](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.sourcerepo_writer](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_iam_member.subnet_viewer](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_project_service.project_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_service) | resource |
| [google_pubsub_topic.budget_notification_topic](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_topic) | resource |
| [google_pubsub_topic.create_project_topic](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_topic) | resource |
| [google_pubsub_topic.increase_budget_topic](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/pubsub_topic) | resource |
| [google_service_account.cl_cloudrun_service_account](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_service_account.cl_function_service_account](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_service_account.cl_tf_service_account](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_service_account_iam_member.org-build-agent](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_service_account_iam_member.org-build-agent-impersonate](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_service_account_iam_member.org-build-impersonate](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_service_account_iam_member.org-build-token](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_service_account_iam_member.tasks_function_user](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_storage_bucket.gcf-source](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |
| [google_storage_bucket.tfstate](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |
| [null_resource.cloudlab_ui_image_builder](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [random_id.proj_id](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [google_dns_managed_zone.cloudlab_dns_zone](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/dns_managed_zone) | data source |
| [google_project.cloudlab_project_data](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/project) | data source |
| [google_service_account.cl_tf_service_account](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/service_account) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_billing_account"></a> [billing\_account](#input\_billing\_account) | GCP Billing Account | `string` | n/a | yes |
| <a name="input_cloud_dns_project"></a> [cloud\_dns\_project](#input\_cloud\_dns\_project) | Managed zone GCP Project ID. | `string` | `null` | no |
| <a name="input_cloud_dns_zone"></a> [cloud\_dns\_zone](#input\_cloud\_dns\_zone) | Managed zone name for Cloud DNS. | `string` | `null` | no |
| <a name="input_cloudlab_project_id"></a> [cloudlab\_project\_id](#input\_cloudlab\_project\_id) | Project ID of an existing project to use for cloudlab infra | `string` | `null` | no |
| <a name="input_cloudlab_project_name"></a> [cloudlab\_project\_name](#input\_cloudlab\_project\_name) | Cloud Lab Builder Project name (not project\_id or number) | `string` | `"cloudlab-infra"` | no |
| <a name="input_create_cloud_dns"></a> [create\_cloud\_dns](#input\_create\_cloud\_dns) | Controls if a Cloud DNS entry is created. If not, DNS must be updated manually | `bool` | `false` | no |
| <a name="input_customer_id"></a> [customer\_id](#input\_customer\_id) | Google Workspace Customer ID for group management. | `string` | `null` | no |
| <a name="input_email_sender"></a> [email\_sender](#input\_email\_sender) | No-reply email address to send emails from. Must match org\_domain. | `string` | `null` | no |
| <a name="input_enable_iap"></a> [enable\_iap](#input\_enable\_iap) | Enable Identity Aware Proxy | `string` | `"false"` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment prefix for Cloud Lab Resources | `string` | `"dev"` | no |
| <a name="input_folder_id"></a> [folder\_id](#input\_folder\_id) | Folder in Org to create Cloud Lab | `string` | n/a | yes |
| <a name="input_group_billing_admins"></a> [group\_billing\_admins](#input\_group\_billing\_admins) | Billing Admin Group | `string` | n/a | yes |
| <a name="input_group_org_admins"></a> [group\_org\_admins](#input\_group\_org\_admins) | Admin Group | `string` | n/a | yes |
| <a name="input_group_prefix"></a> [group\_prefix](#input\_group\_prefix) | Optional suffix to append to group creation. | `string` | `null` | no |
| <a name="input_group_suffix"></a> [group\_suffix](#input\_group\_suffix) | Optional suffix to append to group creation. | `string` | `null` | no |
| <a name="input_host_project"></a> [host\_project](#input\_host\_project) | Optional project ID for the shared VPC host project. | `string` | `null` | no |
| <a name="input_iap_oauth_client"></a> [iap\_oauth\_client](#input\_iap\_oauth\_client) | Identity Aware Proxy oauth Client ID | `string` | `null` | no |
| <a name="input_iap_oauth_secret"></a> [iap\_oauth\_secret](#input\_iap\_oauth\_secret) | Identity Aware Proxy oauth Client Secret | `string` | `null` | no |
| <a name="input_iap_support_email"></a> [iap\_support\_email](#input\_iap\_support\_email) | Identity Aware Proxy support email | `string` | `null` | no |
| <a name="input_identity_service_account"></a> [identity\_service\_account](#input\_identity\_service\_account) | Cloud Lab UI Identity Service Account | `string` | `"cloudlab-ui-identity"` | no |
| <a name="input_is_goog_internal"></a> [is\_goog\_internal](#input\_is\_goog\_internal) | Boolean field used to enable for Google PSO internal testing. | `bool` | `false` | no |
| <a name="input_org_domain"></a> [org\_domain](#input\_org\_domain) | GCP and Workspace domain name | `string` | n/a | yes |
| <a name="input_org_id"></a> [org\_id](#input\_org\_id) | GCP Org ID | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | Prefix for Cloud Lab Resources | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP Region location | `string` | n/a | yes |
| <a name="input_reserved_external_ip"></a> [reserved\_external\_ip](#input\_reserved\_external\_ip) | External global IPv4 address that has already been reserved. | `string` | `null` | no |
| <a name="input_service_account_email"></a> [service\_account\_email](#input\_service\_account\_email) | Service account to use for gcp resources | `string` | `null` | no |
| <a name="input_service_account_project_id"></a> [service\_account\_project\_id](#input\_service\_account\_project\_id) | Project that the external service account lives in. The service account/user deploying code must have appropriate permissions | `string` | `null` | no |
| <a name="input_ssl"></a> [ssl](#input\_ssl) | Provision managed SSL certificate for the HTTPS Load Balancer | `bool` | `true` | no |
| <a name="input_ssl_certificates"></a> [ssl\_certificates](#input\_ssl\_certificates) | SSL certificates used by the HTTP load balaner. | `list(string)` | `[]` | no |
| <a name="input_terraform_sa_name"></a> [terraform\_sa\_name](#input\_terraform\_sa\_name) | Cloud Lab Terraform Service Account | `string` | `"cloudlab-terraform"` | no |
| <a name="input_ui_fqdn"></a> [ui\_fqdn](#input\_ui\_fqdn) | Domain name to run the HTTPS load balancer on | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cloudlab_ar_repo"></a> [cloudlab\_ar\_repo](#output\_cloudlab\_ar\_repo) | Cloudlab Artifact Registry Repository |
| <a name="output_cloudlab_budget_pubsub"></a> [cloudlab\_budget\_pubsub](#output\_cloudlab\_budget\_pubsub) | Cloudlab Budget Notification Pubsub Topic |
| <a name="output_cloudlab_endpoint"></a> [cloudlab\_endpoint](#output\_cloudlab\_endpoint) | IP Address that serves the CloudLab UI |
| <a name="output_cloudlab_folder_id"></a> [cloudlab\_folder\_id](#output\_cloudlab\_folder\_id) | Folder created for end user projects |
| <a name="output_cloudlab_project_id"></a> [cloudlab\_project\_id](#output\_cloudlab\_project\_id) | Cloudlab Infrastructure Project ID |
<!-- END_TF_DOCS -->