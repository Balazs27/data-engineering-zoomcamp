import gzip
from pathlib import Path

import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


CHUNK_SIZE = 200_000

TAXI_DTYPES = {
    'VendorID': 'Int64',
    'passenger_count': 'Int64',
    'trip_distance': 'float64',
    'RatecodeID': 'Int64',
    'store_and_fwd_flag': 'string',
    'PULocationID': 'Int64',
    'DOLocationID': 'Int64',
    'payment_type': 'Int64',
    'fare_amount': 'float64',
    'extra': 'float64',
    'mta_tax': 'float64',
    'tip_amount': 'float64',
    'tolls_amount': 'float64',
    'ehail_fee': 'float64',
    'improvement_surcharge': 'float64',
    'total_amount': 'float64',
    'trip_type': 'Int64',
    'congestion_surcharge': 'float64',
}


@transformer
def transform_green_taxi_2019(data, *args, **kwargs):
    """Clean each monthly Green Taxi file in bounded-memory chunks."""
    year = int(data['year'])
    start = pd.Timestamp(year=year, month=1, day=1)
    end = pd.Timestamp(year=year + 1, month=1, day=1)
    cleaned_dir = Path(data['work_dir']) / 'cleaned'
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    transformed_files = []

    for source in data['files']:
        source_path = Path(source['local_path'])
        output_path = cleaned_dir / source['filename']
        temporary_path = output_path.with_suffix(output_path.suffix + '.part')
        rows_before = 0
        rows_after = 0
        first_chunk = True

        try:
            with gzip.open(
                temporary_path,
                mode='wt',
                encoding='utf-8',
                newline='',
            ) as output_file:
                chunks = pd.read_csv(
                    source_path,
                    compression='gzip',
                    dtype=TAXI_DTYPES,
                    chunksize=int(kwargs.get('chunk_size', CHUNK_SIZE)),
                    low_memory=False,
                )
                for chunk in chunks:
                    required = {
                        'passenger_count',
                        'lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                    }
                    missing = required.difference(chunk.columns)
                    assert not missing, (
                        f'{source_path.name} is missing {sorted(missing)}'
                    )

                    rows_before += len(chunk)
                    pickup = pd.to_datetime(
                        chunk['lpep_pickup_datetime'],
                        errors='coerce',
                    )
                    chunk['lpep_pickup_datetime'] = pickup
                    chunk['lpep_dropoff_datetime'] = pd.to_datetime(
                        chunk['lpep_dropoff_datetime'],
                        errors='coerce',
                    )
                    passenger_count = chunk['passenger_count']
                    keep = (
                        passenger_count.notna()
                        & passenger_count.gt(0)
                        & pickup.ge(start)
                        & pickup.lt(end)
                    )
                    cleaned = chunk.loc[keep].copy()
                    rows_after += len(cleaned)
                    cleaned.to_csv(
                        output_file,
                        index=False,
                        header=first_chunk,
                        date_format='%Y-%m-%d %H:%M:%S',
                    )
                    first_chunk = False

            temporary_path.replace(output_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

        transformed_files.append({
            **source,
            'cleaned_path': str(output_path),
            'rows_before': rows_before,
            'rows_after': rows_after,
            'rows_removed': rows_before - rows_after,
        })

    return {**data, 'files': transformed_files}


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output['files']) == 12
    assert all(item['rows_after'] > 0 for item in output['files'])
    assert all(Path(item['cleaned_path']).exists() for item in output['files'])
