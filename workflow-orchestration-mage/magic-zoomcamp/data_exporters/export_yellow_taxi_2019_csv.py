import gzip
import os
import shutil
from pathlib import Path

from google.cloud import storage

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


COPY_BUFFER_SIZE = 8 * 1024 * 1024


@data_exporter
def export_yellow_taxi_2019_csv(data, *args, **kwargs):
    """Stream twelve cleaned Yellow Taxi CSV files into GCS."""
    project_id = kwargs.get('project_id') or os.environ['GCP_PROJECT_ID']
    bucket_name = kwargs.get('bucket_name') or os.environ['GCS_BUCKET_NAME']
    year = int(data['year'])
    object_prefix = kwargs.get(
        'object_prefix',
        f'nyc_taxi_trips_{year}',
    ).strip('/')

    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    uploaded_files = []

    for item in data['files']:
        cleaned_path = Path(item['cleaned_path'])
        csv_filename = cleaned_path.name.removesuffix('.gz')
        object_name = f'{object_prefix}/{csv_filename}'
        blob = bucket.blob(object_name)
        blob.content_type = 'text/csv'

        with gzip.open(cleaned_path, mode='rb') as source_file:
            with blob.open(
                mode='wb',
                chunk_size=COPY_BUFFER_SIZE,
                timeout=600,
            ) as destination_file:
                shutil.copyfileobj(
                    source_file,
                    destination_file,
                    length=COPY_BUFFER_SIZE,
                )

        uploaded_files.append({
            'month': item['month'],
            'rows': item['rows_after'],
            'uri': f'gs://{bucket_name}/{object_name}',
        })

    return {
        'project_id': project_id,
        'bucket_name': bucket_name,
        'object_prefix': object_prefix,
        'files': uploaded_files,
    }


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output['files']) == 12
    assert all(item['uri'].endswith('.csv') for item in output['files'])
