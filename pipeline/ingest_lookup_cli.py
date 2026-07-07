#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click


dtype = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string"
}


@click.command()
@click.option('--pg-user', default='root', show_default=True, help='PostgreSQL user')
@click.option('--pg-password', default='root', show_default=True, help='PostgreSQL password')
@click.option('--pg-host', default='localhost', show_default=True, help='PostgreSQL host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='PostgreSQL port')
@click.option('--pg-database', default='ny_taxi', show_default=True, help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_location_lookup', show_default=True, help='Target table name')
@click.option('--csv-path', default='taxi_zone_lookup.csv', show_default=True, help='Path to local CSV file')
@click.option('--chunksize', default=100000, show_default=True, type=int, help='Number of rows per chunk')
def run(pg_user, pg_password, pg_host, pg_port, pg_database, target_table, csv_path, chunksize):
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f'CSV file not found: {path}')

    engine = create_engine(
        f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'
    )

    df_iter = pd.read_csv(
        path,
        dtype=dtype,
        iterator=True,
        chunksize=chunksize
    )

    # ITERATE OVER CHUNKS AND INSERT DATA
    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(n=0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace',
                index=False
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append',
            index=False
        )


if __name__ == '__main__':
    run()