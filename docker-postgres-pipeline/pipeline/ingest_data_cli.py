#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='root', show_default=True, help='PostgreSQL user')
@click.option('--pg-password', default='root', show_default=True, help='PostgreSQL password')
@click.option('--pg-host', default='localhost', show_default=True, help='PostgreSQL host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='PostgreSQL port')
@click.option('--pg-database', default='ny_taxi', show_default=True, help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_trips', show_default=True, help='Target table name')
@click.option('--year', default=2021, show_default=True, type=int, help='Taxi data year')
@click.option('--month', default=1, show_default=True, type=int, help='Taxi data month')
@click.option('--chunksize', default=100000, show_default=True, type=int, help='Number of rows per chunk')
def run(pg_user, pg_password, pg_host, pg_port, pg_database, target_table, year, month, chunksize):
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'

    engine = create_engine(
        f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'
    )

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
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