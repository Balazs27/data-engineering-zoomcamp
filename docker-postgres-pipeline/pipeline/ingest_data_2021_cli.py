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


def month_range(start_year, start_month, end_year, end_month):
    year = start_year
    month = start_month

    while (year, month) <= (end_year, end_month):
        yield year, month

        month += 1

        if month == 13:
            month = 1
            year += 1


@click.command()
@click.option('--pg-user', default='root', show_default=True, help='PostgreSQL user')
@click.option('--pg-password', default='root', show_default=True, help='PostgreSQL password')
@click.option('--pg-host', default='localhost', show_default=True, help='PostgreSQL host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='PostgreSQL port')
@click.option('--pg-database', default='ny_taxi', show_default=True, help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_trips', show_default=True, help='Target table name')
@click.option('--start-year', default=2021, show_default=True, type=int, help='Start year')
@click.option('--start-month', default=1, show_default=True, type=int, help='Start month')
@click.option('--end-year', default=2021, show_default=True, type=int, help='End year')
@click.option('--end-month', default=1, show_default=True, type=int, help='End month')
@click.option('--chunksize', default=100000, show_default=True, type=int, help='Number of rows per chunk')
@click.option(
    '--if-exists',
    default='replace',
    show_default=True,
    type=click.Choice(['replace', 'append']),
    help='What to do if the target table already exists'
)
def run(
    pg_user,
    pg_password,
    pg_host,
    pg_port,
    pg_database,
    target_table,
    start_year,
    start_month,
    end_year,
    end_month,
    chunksize,
    if_exists
):
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'

    engine = create_engine(
        f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'
    )

    first_write = True

    for year, month in month_range(start_year, start_month, end_year, end_month):
        url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'

        print(f'Ingesting {url}')

        df_iter = pd.read_csv(
            url,
            dtype=dtype,
            parse_dates=parse_dates,
            iterator=True,
            chunksize=chunksize
        )

        for df_chunk in tqdm(df_iter, desc=f'{year}-{month:02d}'):
            # Useful metadata columns
            df_chunk['source_year'] = year
            df_chunk['source_month'] = month

            if first_write:
                df_chunk.head(n=0).to_sql(
                    name=target_table,
                    con=engine,
                    if_exists=if_exists,
                    index=False
                )
                first_write = False

            df_chunk.to_sql(
                name=target_table,
                con=engine,
                if_exists='append',
                index=False
            )

    print('Ingestion finished.')


if __name__ == '__main__':
    run()