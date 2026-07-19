import os

from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from mage_ai.settings.repo import get_repo_path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_single_parquet(data, *args, **kwargs) -> None:
    """Export the transformed month as one Parquet object."""
    bucket_name = kwargs.get('bucket_name') or os.environ['GCS_BUCKET_NAME']
    object_key = kwargs.get('object_key', 'nyc_taxi_data.parquet')
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')

    GoogleCloudStorage.with_config(
        ConfigFileLoader(config_path, 'default')
    ).export(data, bucket_name, object_key)
