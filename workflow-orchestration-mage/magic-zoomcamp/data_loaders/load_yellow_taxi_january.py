import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


DEFAULT_URL = (
    'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
    'yellow/yellow_tripdata_2021-01.csv.gz'
)

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
    'improvement_surcharge': 'float64',
    'total_amount': 'float64',
    'congestion_surcharge': 'float64',
}


@data_loader
def load_yellow_taxi_january(*args, **kwargs):
    """Load one month of Yellow Taxi trips into a pandas DataFrame."""
    url = kwargs.get('source_url', DEFAULT_URL)
    return pd.read_csv(
        url,
        compression='gzip',
        dtype=TAXI_DTYPES,
        parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'],
    )


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert not output.empty, 'The source dataset is empty'
    assert 'tpep_pickup_datetime' in output.columns
