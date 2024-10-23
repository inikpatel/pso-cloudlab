# Cloud Lab Templates

The following Cloud Lab templates are supported or planed:

## default

This template creates a default project with the following services enabled:

  - aiplatform.googleapis.com
  - cloudbilling.googleapis.com
  - compute.googleapis.com
  - dataform.googleapis.com
  - iap.googleapis.com
  - monitoring.googleapis.com
  - networkmanagement.googleapis.com
  - networkconnectivity.googleapis.com
  - notebooks.googleapis.com
  - serviceusage.googleapis.com
  - stackdriver.googleapis.com
  - storage.googleapis.com
  - workstations.googleapis.com

The requestor of the project will have the following roles:

    - roles/editor
    - roles/workstations.admin
    - roles/compute.networkUser
    - roles/iap.tunnelResourceAccessor
    - roles/iap.httpsResourceAccessor
    - roles/aiplatform.admin
    - roles/logging.viewAccessor
    - roles/logging.viewer
    - roles/source.admin
    - roles/cloudaicompanion.user


## cloud-storage

This template creates a default project and a Cloud Storage bucket, with the following additional services enable in addition to the default ones:

  - orgpolicy.googleapis.com
  - servicenetworking.googleapis.com
  - storage-component.googleapis.com

And also these additional roles assigned to the requestor:

  - roles/storage.admin
  - roles/storage.objectAdmin

# data-playground

This templates creates a minimum viable architecture for a data experimentation project with the needed APIs enabled, VPC and Firewall set in place, BigQuery dataset, GCS bucket and an AI notebook to get started.

The additional services enabled are:

  - bigquery.googleapis.com
  - bigquerystorage.googleapis.com
  - bigqueryreservation.googleapis.com
  - composer.googleapis.com
  - dialogflow.googleapis.com
  - ml.googleapis.com
  - orgpolicy.googleapis.com
  - servicenetworking.googleapis.com
  - storage-component.googleapis.com

The additional roles granted to the requestor are:

    - roles/storage.admin
    - roles/storage.objectAdmin
    - roles/bigquery.admin

    (Additional ones may be added later)
