import os

import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import fs

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_january_daily_partitions(data, *args, **kwargs) -> None:
    """Write a GCS Parquet dataset partitioned by pickup date."""
    bucket_name = kwargs.get('bucket_name') or os.environ['GCS_BUCKET_NAME']
    object_prefix = kwargs.get(
        'object_prefix',
        'yellow_taxi_2021_01_daily',
    ).strip('/')

    partitioned = data.copy()
    partitioned['tpep_pickup_date'] = (
        partitioned['tpep_pickup_datetime'].dt.date
    )

    table = pa.Table.from_pandas(partitioned, preserve_index=False)
    filesystem = fs.GcsFileSystem()
    pq.write_to_dataset(
        table,
        root_path=f'{bucket_name}/{object_prefix}',
        partition_cols=['tpep_pickup_date'],
        filesystem=filesystem,
    )
