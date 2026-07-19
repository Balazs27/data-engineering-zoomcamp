# Data Engineering Zoomcamp

This repository documents my progress through the
[DataTalks.Club Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp).
I am building practical data engineering skills around the NYC Taxi dataset,
following the data from ingestion and cloud storage through warehouse
transformations and reporting.

The project currently demonstrates this batch data flow:

```text
NYC Taxi data → Python and Mage → GCS → BigQuery → dbt → Looker Studio
```

## Completed modules

### Module 1: Containerization and infrastructure

In the [Docker and PostgreSQL pipeline](./docker-postgres-pipeline/README.md), I
built a containerized Python ingestion workflow and loaded NYC Taxi data into a
local PostgreSQL database managed with Docker and pgAdmin.

The [Terraform module](./terraform/README.md) provisions the Google Cloud
Storage bucket and BigQuery dataset used by the cloud pipeline while keeping
credentials, state, and environment-specific values outside version control.

### Module 2: Workflow orchestration

The [Mage orchestration module](./workflow-orchestration-mage/README.md)
contains reusable extraction and loading pipelines for CSV and Parquet data,
including scheduled daily files, date-based partitions, and batch ingestion
into GCS and BigQuery.

### Module 3: Data warehousing

The [BigQuery module](./data-warehousing-big-query/README.md) explores external
tables, native tables, partitioning, and clustering. It includes SQL examples
that compare query behavior and demonstrate how warehouse design can reduce
the amount of data scanned.

### Module 4: Analytics engineering

The [dbt analytics project](./dbt_project/README.md) transforms raw Green and
Yellow Taxi data into tested and documented staging, intermediate, fact,
dimension, and reporting models, followed by a small Looker Studio dashboard.

## Coming next

I am currently completing the remaining Zoomcamp modules:

- batch processing with Apache Spark;
- stream processing with Apache Kafka.

Their implementations and learning notes will be added to this repository once
each module is complete.
