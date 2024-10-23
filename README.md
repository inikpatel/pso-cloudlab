# Cloud Lab Terraform Repo

This repo contains the scripting to build the backend infrastructure project for Cloud Lab, as well as a sample `cloudlab-repo` project that Cloud Lab actually uses to provision the user projects.

## Cloud Lab architecture

The diagram below shows the Cloud Lab architecture:

![](./cloudlab.svg)


## Cloud Lab infrastructure

The Cloud Lab backend infrastructure project is available as a Terraform module under `terraform/modules/cloudlab`, there are other dependencies also under `terraform/modules`.

Under `environments/dev`, a `config` sub-directory contains a YAML based configuration file which replaces the regular terraform.tfvars file to define the Cloud lab settings. Follow the instructions in `cloudlab.yaml.template` to create a new configuration file.

Create a Terraform project under `environments/<env>`, and create the required providers, backends, etc. components, and in the `main.tf` file passing all the required variables to the `cloudlab` module. 

```
locals {
  cfg = yamldecode(file("./config/cloudlab.yaml"))
}

module "cloudlab-inf" {
  source = "../../modules/cloudlab"

  cloudlab_project_name = local.cfg.cloudlab_project_name
  cloudlab_project_id   = try(local.cfg.cloudlab_project_id, null)

  prefix                     = local.cfg.prefix
  region                     = local.cfg.region
  org_id                     = local.cfg.org_id
  folder_id                  = local.cfg.folder_id
  billing_account            = local.cfg.billing_account
  group_org_admins           = local.cfg.group_org_admins
  group_billing_admins       = local.cfg.group_billing_admins
  service_account_email      = try(local.cfg.service_account_email, null)
  service_account_project_id = try(local.cfg.service_account_project_id, null)
  identity_service_account   = local.cfg.identity_service_account
  environment                = local.cfg.environment
  org_domain                 = local.cfg.org_domain
  ssl_certificates           = try(local.cfg.ssl_certificates, null)
  enable_iap                 = local.cfg.enable_iap
  iap_support_email          = try(local.cfg.iap_support_email, "")
  ui_fqdn                    = try(local.cfg.ui_fqdn, null)
  iap_oauth_client           = try(local.cfg.iap_oauth_client, null)
  iap_oauth_secret           = try(local.cfg.iap_oauth_secret, null)

}
```

The Cloud Lab infrastructure provisions the following cloud resources:

- Cloud Lab project `prj-cloudlab-<env>` with following services:

  - **Firestore database**: `default` stores user input;
  - **Cloud Run application**: `cloud-lab-ui` interacts with user;
  - **Cloud Functions**: `git-push-http-fn` and `create_project_fn`, etc.;
  - **Pubsub Topics**: `prj-cloudlab-create-proj-topic-<env>`, `prj-cloudlab-budget-notification-topic-<env>`, etc.;
  - **Cloud Build service and trigger**: `cloudlab-projects`;
  - **Cloud Source Repository**: `cloudlab-repo`;
  - **Artifact Registry repositories**: `cloudlab-ui` and `gcf-artifacts`;
  - **Cloud Storage Buckets**: for cloud build, cloud run, cloud functions, Terraform state files, etc.;
  - **Cloud Load Blanacer**: `cloud-lab-ui-https-proxy` and SSL certificate;

The above resources are relatively stable once deployed, unless there are updates in the Cloud Lab UI or functions.

The Cloud Lab infrastructure can be deployed manually or integrated with a CICD workflow, we will describe these two processes in later sections.

## Cloud Lab user projects

The [`cloudlab-repo`](./repo-code) sub-directory contains the Terraform script that provisions the user projects. It needs to be uploaded to the Cloud Source Repository created by the Cloud Lab infrastructure code above first, then the Cloud Functions will take care of the workflow from Cloud Lab UI to the actual deployment of the projects.

An automated CICD workflow has been created via Cloud Functions and Pub/Sub topics, but regular check of Cloud Build history is highly recommended to detect any errors or exceptions.

Please refer to the [README.md](./repo-code/README.md) file under the `cloudlab-repo` sub-directory on how to set up and initialize the repo in Cloud Source Respitory service.


## Dependencies

This README assumes you have installed and configured the following

- `terraform`, version 1.8.1
- `gcloud`, latest version

## Manual Deployment of Cloud Lab Infrastructure Instructions

1. Clone this repo via `git` or `gcloud` command:
   ```shell
   git clone <repo url>
   cd <repo name>
   ```

   or 

   ```shell
   gcloud source repos clone <repo name>
   cd <repo name>
   ```

2. Change directory to `terraform/environments`, create a sub-directory representing the environment (dev, np, or prod), and create a configuration file `config/cloudlab.yaml` from the template file.

   * Fill out the `cloudlab.yaml` file with your environment specific variables.

        * `project_id`: The project id to use for the Cloud Lab infrastructure.
        * `prefix`: A up to 4 character prefix to append to most resources and end user projects.
        * `region`: The desired GCP region, such as `us-east4`.
        * `org_id`: The GCP Org id number.
        * `folder_id`: The parent GCP folder id to place the Cloud Lab infrastructure. This is separate from the `project` folder detailed below.
        * `billing_account`: A GCP Billing Account ID to use for all Cloud Lab Projects
        * `cloudlab_developers`: A google group for all Cloud Lab Developers. This group will be given control of development environments, and read access to higher level environments.
        * `cloudlab_admins`: A google group for all administrators of Cloud Lab. This group will be given control of all Cloud Lab infrastructure.

    * DNS Considerations: Configure the following DNS settings if you want the terraform to automatically create DNS A records in a Cloud DNS managed zone. Do not set these values if you want to control DNS manually.
        * `create_cloud_dns`: An optional boolean field, controls if Cloud DNS Records are created
        * `cloud_dns_zone` : Cloud DNS managed zone name. Required if `create_cloud_dns` = `true`
        * `cloud_dns_project`: GCP Project ID where the `cloud_dns_zone` resides.

3. From the root directory, run:
    ```shell
    terraform init
    terraform plan
    terraform apply
    ```
    NOTE: The managed HTTPS certificate relies on a valid DNS entry, and takes some time (up to 24 hours) to become available immediately after creation.

4. After creating the Cloud Lab infrastructure with the above terraform, you will have to seed the Cloud Lab source repository with the contents of the `repo-code` folder.
This folder contains the terraform code which is responsible for constructing the individual Cloud Lab projects for end users.

    Perform the following steps to seed the repo, where `<projectid>` is the project id returned in the outputs from the `terrafrom apply`:

    ```shell
    gcloud source repos clone cloudlab-repo --project=<projectid>
    cd cloudlab-repo/
    cp -r ../repo-code/. .
    ```

    Modify the CloudLab default template files located at `cloudlab-repo/data/templates/cloudlab.yaml.template` and set the following variables specific to your environment:
    * `billing_account_id` `billing_account_id` Sets the deisred billing ID for all projects
    * `billing_alert.amount` Sets the budget cap for your projects.
    * `pubsub_topic` is the `cloudlab_budget_pubsub` output value from step 3.
    * `essential_contacts` An admin group to recieve budget and various platform alerts.
    * `services` Is a list of API's to enable by default for all projects.

    Once complete, commit the default changes with the following:
    ```shell
    git add .
    git commit -m "Initial load of CloudLab Repo"
    git push origin main
    ```

5.  To activate IAP for the CloudLab UI, some additional manual steps are required:

    * Create an IAP oauth client ID and secret using the IAP brand ID that was created by terraform:

    ```shell
    gcloud iap oauth-brands create --application_title cloudlab --support_email "your_support_email@domain.com"

    gcloud iap oauth-clients create `gcloud iap oauth-brands list --format 'value(name)'` --display_name="CloudLab IAP Client"

    gcloud beta services identity create --service=iap.googleapis.com
    ```

    The response contains the following fields:

    ```
    name: projects/[PROJECT_NUMBER]/brands/[BRAND_NAME]/identityAwareProxyClients/[CLIENT_ID]
    secret: [CLIENT_SECRET]
    displayName: [NAME]
    ```

    * Once the above steps are completed, enter the values in the `config/cloudlab.yaml` file for IAP specific settings:
        * `enable_iap`: An optional boolean field, can only be enabled after the initial terraform is complete
        * `iap_support_email`: A valid user or group email address to be used for enabling IAP.
        * `iap_oauth_client`: Obtained manually after initial terraform configuration is complete
        * `iap_oauth_secret`: Obtained manually after initial terraform configuration is complete

    Use the client ID (client_id in the above example) and secret value and enter it in the appropriate section of the terraform.tfvars file, and run `terraform plan` and then `terraform apply` to enable IAP.

    Users accessing the application need the `IAP-Secured Web App User Role`.

### Detailed Cloud Lab Infrastructure Terraform Config

See detailed information in the [Cloud Lab module README](terraform/modules/cloudlab/README.md).
