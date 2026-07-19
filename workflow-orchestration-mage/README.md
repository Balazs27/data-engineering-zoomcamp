# Workflow Orchestration with Mage

This module contains my workflow-orchestration exercises from the Data
Engineering Zoomcamp. I used Mage to turn individual extraction,
transformation, and loading blocks into reproducible NYC Taxi pipelines.

The published project contains pipeline definitions and source code only.
Credentials, local connection settings, Mage runtime data, cached block
outputs, and downloaded datasets are intentionally excluded.

## What I built

| Pipeline | Extract | Transform | Load |
| --- | --- | --- | --- |
| `taxi_single_parquet` | January 2021 Yellow Taxi CSV from the course dataset | Parse timestamps and remove trips with zero passengers | One Parquet object in GCS |
| `taxi_scheduled_daily_parquet` | January 2021 Yellow Taxi CSV | Apply the same quality checks | One Parquet object under an execution-date path |
| `taxi_january_daily_partitions` | January 2021 Yellow Taxi CSV | Apply the same quality checks | A PyArrow dataset partitioned by `tpep_pickup_date` |
| `green_taxi_2019_csv_batch` | Twelve monthly 2019 Green Taxi CSV files | Clean each file in chunks and validate its year | Twelve monthly CSV objects in GCS |
| `yellow_taxi_2019_csv_batch` | Twelve monthly 2019 Yellow Taxi CSV files | Clean each file in chunks and validate its year | Twelve monthly CSV objects in GCS |

The two 2019 CSV batch pipelines prepare the source files used later in the
BigQuery and dbt modules. In that workflow, the GCS objects are exposed through
BigQuery external tables, converted into native partitioned tables, and then
used as dbt sources.

## What I learned

- How an orchestrator models loaders, transformers, exporters, dependencies,
  and pipeline runs
- How to separate pipeline code from credentials and environment-specific
  configuration
- How execution dates can drive deterministic object paths
- The difference between writing one Parquet object and a partitioned Parquet
  dataset
- How date partitioning creates one logical partition per pickup date
- How to process a full year without keeping the entire dataset in memory
- How chunked transforms and streaming uploads limit worker memory and disk use
- How orchestration connects ingestion in GCS to downstream BigQuery and dbt
  workflows

## Project structure

```text
workflow-orchestration-mage/
├── README.md
├── Dockerfile
├── docker-compose.yaml
├── dev.env
├── requirements.txt
└── magic-zoomcamp/
    ├── data_loaders/
    ├── transformers/
    ├── data_exporters/
    ├── pipelines/
    ├── io_config.yaml.template
    ├── metadata.yaml
    └── requirements.txt
```

Mage stores each block in its block-type directory. Each
`pipelines/<pipeline>/metadata.yaml` file records the block graph and upstream
dependencies required to reconstruct that pipeline.

## Local setup

Copy the development template:

```bash
cp dev.env .env
```

Edit the ignored `.env` and set:

- `GCP_PROJECT_ID`
- `GCS_BUCKET_NAME`
- `GOOGLE_SERVICE_ACCOUNT_KEY_PATH`

If using a local service-account key for this learning environment, place it
inside the ignored `keys/` directory. The Compose configuration mounts the file
read-only at a generic container path. Never commit the key.

Create the local Mage IO configuration:

```bash
cp magic-zoomcamp/io_config.yaml.template magic-zoomcamp/io_config.yaml
```

Start Mage and PostgreSQL:

```bash
docker compose up --build
```

Mage is then available at <http://localhost:6789>.

Stop the services:

```bash
docker compose down
```

Add `--volumes` only when the local PostgreSQL data should also be deleted.

## Configuration and security

The real `.env`, `io_config.yaml`, service-account keys, Mage database,
execution history, cached outputs, and generated data files are ignored.

The committed `dev.env` contains local-development defaults and public
placeholders only. The committed `io_config.yaml.template` resolves credentials
and database settings from environment variables. Cloud identifiers and key
paths are not embedded in pipeline source code.

For a deployed system, prefer short-lived identity mechanisms such as workload
identity or Application Default Credentials over downloadable service-account
keys.
