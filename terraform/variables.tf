variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Default GCP region"
  type        = string
  default     = "europe-west1"
}

variable "location" {
  description = "Location for the GCS bucket and BigQuery dataset"
  type        = string
  default     = "EU"
}

variable "bq_dataset_name" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "gcs_bucket_name" {
  description = "Globally unique GCS bucket name"
  type        = string
}

variable "gcs_storage_class" {
  description = "GCS bucket storage class"
  type        = string
  default     = "STANDARD"
}
