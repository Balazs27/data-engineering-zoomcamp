# Terraform Quickstart Guide

This guide explains the Terraform concepts behind the Data Engineering Zoomcamp module and why Terraform matters for data engineering work.

## What Terraform Is

Terraform is an infrastructure as code tool.

Instead of creating infrastructure manually in the cloud console, you describe the desired infrastructure in `.tf` files. Terraform then talks to the cloud provider APIs and creates, updates, or deletes the real resources.

In the Zoomcamp module, the infrastructure is small:

- one Google Cloud Storage bucket
- one BigQuery dataset

You could create both manually in the GCP UI. Terraform becomes valuable when the infrastructure grows, needs to be repeated, reviewed, shared, or recreated reliably.

## Why Not Just Use the GCP UI?

The UI is fine for exploration. It is not ideal for repeatable engineering work.

With manual clicks:

- It is easy to forget a setting.
- It is hard to know exactly what changed.
- Recreating the same setup in another project is tedious.
- Reviewing infrastructure changes is difficult.
- Cleanup depends on remembering what you created.

With Terraform:

- Infrastructure is declared in code.
- Changes can be reviewed in Git.
- The same setup can be recreated across dev, staging, and production.
- Terraform shows a plan before changing resources.
- Teams can standardize cloud resources and naming.
- Disaster recovery is easier because infrastructure can be recreated from code.

Terraform does not remove the need to understand the cloud. It gives you a safer and more repeatable way to manage it.

## Core Terraform Concepts

### Provider

A provider is the plugin Terraform uses to talk to a platform.

For GCP:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}
```

The provider block tells Terraform:

- which GCP project to use
- which region to use by default

The Google provider uses Application Default Credentials (ADC) for
authentication. For local development, authenticate with your user account:

```bash
gcloud auth application-default login
```

If a service account key is required for this learning environment, keep the
JSON file inside the ignored `keys/` directory and point ADC to it for the
current shell:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/keys/your-service-account-key.json"
```

Never put the key contents, key filename, or a machine-specific absolute path
in committed Terraform files.

### Resource

A resource is something Terraform manages.

Example:

```hcl
resource "google_storage_bucket" "demo_bucket" {
  name     = var.gcs_bucket_name
  location = var.location
}
```

This means: create and manage a GCS bucket.

The first string, `google_storage_bucket`, is the resource type.

The second string, `demo_bucket`, is Terraform's local name for this resource.

### Variables

Variables let you avoid hardcoding values in `main.tf`.

Example:

```hcl
variable "project" {
  description = "GCP project ID"
  type        = string
}
```

Then in `main.tf`:

```hcl
project = var.project
```

This makes the code easier to reuse. For example, you can keep the same Terraform code but pass a different project, region, bucket name, or dataset name.

The project ID, bucket name, and dataset name are environment-specific inputs.
Store their real local values in an ignored `terraform.tfvars` file:

```hcl
project          = "your-gcp-project-id"
gcs_bucket_name  = "your-globally-unique-bucket-name"
bq_dataset_name  = "your_bigquery_dataset"
```

Terraform loads `terraform.tfvars` automatically. The file is intentionally
ignored so the committed module remains reusable and does not publish
environment metadata.

### State

Terraform keeps a state file, usually `terraform.tfstate`, that maps your `.tf` code to real cloud resources.

State answers questions like:

- Which bucket did Terraform create?
- Which dataset belongs to this Terraform project?
- What changed since the last apply?

State is important. Do not casually delete or edit it.

For serious team projects, Terraform state is usually stored remotely, for example in a GCS bucket. For the Zoomcamp, local state is fine while learning.

### Plan

`terraform plan` shows what Terraform intends to do before it does it.

Use it every time:

```bash
terraform plan
```

Read the output. Look for creates, updates, and deletes.

### Apply

`terraform apply` executes the plan:

```bash
terraform apply
```

Terraform will ask for confirmation before changing infrastructure.

### Destroy

`terraform destroy` deletes resources managed by the current Terraform state:

```bash
terraform destroy
```

This is useful while learning because you can clean up GCS buckets, BigQuery datasets, and other resources when you are done.

Be careful in real projects. Destroying production infrastructure is serious.

## Terraform Workflow

Typical local workflow:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Cleanup workflow:

```bash
terraform destroy
```

What each command does:

- `terraform init`: downloads providers and prepares the working directory.
- `terraform fmt`: formats `.tf` files.
- `terraform validate`: checks syntax and basic configuration validity.
- `terraform plan`: previews changes.
- `terraform apply`: makes changes.
- `terraform destroy`: deletes managed resources.

## How Terraform Is Used in Data Engineering

Data engineering pipelines need infrastructure:

- object storage buckets for data lakes
- data warehouse datasets and tables
- service accounts and IAM permissions
- workflow orchestration infrastructure
- Pub/Sub topics
- Kafka clusters or managed streaming services
- Dataproc/Spark clusters
- Cloud Run jobs
- Composer/Airflow environments
- secrets and environment variables
- monitoring and alerting resources

Terraform lets teams define these resources in a repeatable way.

For example, a data platform team might use Terraform to create:

- a raw GCS bucket
- a staging GCS bucket
- a curated GCS bucket
- BigQuery datasets for `raw`, `staging`, `analytics`, and `mart`
- service accounts for Airflow, dbt, and ingestion jobs
- IAM rules so each service has only the permissions it needs
- scheduled jobs or orchestration infrastructure

The ETL/ELT code then runs on top of infrastructure that is already standardized.

## How Terraform Is Used in Industry

In many companies, Terraform is used through Git and CI/CD.

A common workflow:

1. Engineer changes Terraform code.
2. Engineer opens a pull request.
3. CI runs `terraform fmt`, `terraform validate`, and `terraform plan`.
4. Team reviews the infrastructure change.
5. After approval, CI/CD runs `terraform apply`.
6. Terraform state is stored remotely and locked to avoid concurrent edits.

This creates an audit trail:

- who changed infrastructure
- what was changed
- when it changed
- why it changed

That is much better than undocumented console clicks.

## Terraform and DevOps

In companies with a dedicated DevOps, platform, or cloud infrastructure team, that team often owns the core Terraform setup.

They may manage:

- networks
- IAM foundations
- production environments
- Kubernetes clusters
- shared CI/CD infrastructure
- security policies
- remote state
- reusable Terraform modules

Data engineers may still use Terraform for data-specific resources:

- GCS buckets
- BigQuery datasets
- Pub/Sub topics
- service accounts for pipelines
- scheduled jobs
- data platform resources

So Terraform can be either:

- mostly owned by DevOps/platform teams
- shared between platform and data teams
- owned by data engineers in smaller companies

For data engineering job ads, Terraform as "nice to have" usually means: you do not need to be a full DevOps engineer, but you should understand infrastructure as code and be comfortable reading or making small Terraform changes.

## Benefits for Your Capstone

For your NYC taxi capstone, Terraform can help you show professional engineering habits.

A good Terraform scope:

- GCS bucket for raw data
- GCS bucket or prefix for processed data
- BigQuery datasets such as `raw`, `staging`, `analytics`
- service account for orchestration
- IAM permissions for the pipeline

This makes your project easier to explain:

- Terraform provisions the cloud infrastructure.
- Orchestration extracts and loads data.
- BigQuery stores warehouse tables.
- dbt transforms the data.
- Looker Studio visualizes the curated tables.

That story is stronger than "I clicked around in the UI and uploaded files."

## Safety Notes

Never commit service account keys.

Keep these ignored:

```gitignore
keys/
*.json
*.tfvars
*.tfvars.json
*.tfstate
*.tfstate.*
.terraform/
```

The project ID, bucket name, and dataset name are not credentials and do not
grant access by themselves; IAM controls access. They are still useful
environment metadata, and GCS bucket names are globally unique and publicly
visible, so this module keeps the real values in local variable files.

Terraform state can contain resource metadata and sensitive values in plain
text. Keep local state and its backups out of Git; use a protected remote
backend for shared or production infrastructure.

Also be careful with `force_destroy = true` on GCS buckets. It lets Terraform delete a bucket even if it contains objects. That is convenient while learning, but risky in production.

## Mental Model

Terraform is not the data pipeline.

Terraform creates the infrastructure that the data pipeline uses.

For the Zoomcamp:

- Terraform creates GCS and BigQuery resources.
- Kestra, Mage, Airflow, or Prefect load data into those resources.
- BigQuery and dbt transform/query the data.

Keep that separation clear and Terraform will make much more sense.
