terraform {

  backend "gcs" {
    #Replace with command line -vars
    #bucket = ''
    #impersonate_service_account = var.service_account_email

  }
}
