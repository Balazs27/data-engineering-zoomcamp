# Docker and PostgreSQL Data Pipeline

This folder contains my work for the first module of the Data Engineering
Zoomcamp. The module introduces the foundations of a local data engineering
environment by running PostgreSQL and pgAdmin with Docker and loading NYC Taxi
data into the database with a containerized Python pipeline.

## What I built

- A Docker Compose stack with PostgreSQL, pgAdmin, and a reusable ingestion
  service
- A Docker image for the Python ingestion pipeline
- Command-line scripts that download NYC Yellow Taxi trip data and load it into
  PostgreSQL in chunks
- A second ingestion script for the taxi zone lookup table
- A multi-month ingestion script for loading a configurable date range
- A Jupyter notebook for exploring the source data and testing the ingestion
  workflow
- A small introductory Python exercise in `pipeline/test/`

## What I learned

- How containers, images, volumes, ports, and Docker networks work
- How to run PostgreSQL and pgAdmin as persistent Docker services
- How to connect services to each other with Docker Compose
- How to package and run a Python data pipeline in a container
- How to use pandas and SQLAlchemy to create tables and insert data into
  PostgreSQL
- How to process larger datasets incrementally with chunked ingestion
- How to expose configuration through a command-line interface with Click
- How to manage and lock Python dependencies with `uv`

## Project structure

```text
docker-postgres-pipeline/
├── README.md
└── pipeline/
    ├── Dockerfile
    ├── docker-compose.yaml
    ├── ingest_data_cli.py
    ├── ingest_data_2021_cli.py
    ├── ingest_lookup_cli.py
    ├── NYC_Taxi_Notebook.ipynb
    ├── taxi_zone_lookup.csv
    ├── pyproject.toml
    ├── uv.lock
    └── test/
```

## Running the module

Run the following commands from the `pipeline/` directory.

Start PostgreSQL and pgAdmin:

```bash
docker compose up -d pgdatabase pgadmin
```

pgAdmin is available at <http://localhost:8085>. The PostgreSQL server is
available on `localhost:5432`.

Load one month of NYC Yellow Taxi data:

```bash
docker compose run --rm ingest ingest_data_cli.py \
  --pg-host pgdatabase \
  --year 2021 \
  --month 1
```

Load the taxi zone lookup table:

```bash
docker compose run --rm ingest ingest_lookup_cli.py \
  --pg-host pgdatabase \
  --csv-path /data/taxi_zone_lookup.csv
```

Load a range of months:

```bash
docker compose run --rm ingest ingest_data_2021_cli.py \
  --pg-host pgdatabase \
  --start-year 2021 \
  --start-month 1 \
  --end-year 2021 \
  --end-month 12
```

Stop the services:

```bash
docker compose down
```

Add `--volumes` to the final command only when the stored PostgreSQL and pgAdmin
data should also be deleted.
