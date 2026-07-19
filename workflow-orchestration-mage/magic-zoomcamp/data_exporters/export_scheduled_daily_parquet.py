import os

from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from mage_ai.settings.repo import get_repo_path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_scheduled_daily_parquet(data, *args, **kwargs) -> None:
    """Write one Parquet object under the Mage execution-date path."""
    execution_date = kwargs.get('execution_date')
    assert execution_date is not None, 'Mage execution_date is required'

    bucket_name = kwargs.get('bucket_name') or os.environ['GCS_BUCKET_NAME']
    object_key = (
        f'{execution_date:%Y/%m/%d}/daily_trips.parquet'
    )
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')

    GoogleCloudStorage.with_config(
        ConfigFileLoader(config_path, 'default')
    ).export(data, bucket_name, object_key)
