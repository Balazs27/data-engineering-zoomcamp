from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


BASE_URL = (
    'https://github.com/DataTalksClub/nyc-tlc-data/'
    'releases/download/yellow'
)
DEFAULT_YEAR = 2019
DEFAULT_WORK_DIR = '/tmp/mage_nyc_taxi/yellow'


def _download(url: str, destination: Path) -> None:
    """Download a file atomically and retry transient HTTP failures."""
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=('GET',),
    )
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry))
    temporary_path = destination.with_suffix(destination.suffix + '.part')

    try:
        with session.get(url, stream=True, timeout=(30, 600)) as response:
            response.raise_for_status()
            with temporary_path.open('wb') as output_file:
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        output_file.write(block)

        with temporary_path.open('rb') as downloaded_file:
            assert downloaded_file.read(2) == b'\x1f\x8b', (
                f'{url} did not return a gzip file'
            )
        temporary_path.replace(destination)
    finally:
        session.close()
        if temporary_path.exists():
            temporary_path.unlink()


@data_loader
def load_yellow_taxi_2019(*args, **kwargs):
    """Stage twelve compressed monthly Yellow Taxi files on the worker."""
    year = int(kwargs.get('year', DEFAULT_YEAR))
    work_dir = Path(kwargs.get('work_dir', DEFAULT_WORK_DIR)) / str(year)
    download_dir = work_dir / 'downloaded'
    download_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for month in range(1, 13):
        filename = f'yellow_tripdata_{year}-{month:02d}.csv.gz'
        url = f'{BASE_URL}/{filename}'
        local_path = download_dir / filename

        if not local_path.exists() or local_path.stat().st_size == 0:
            print(f'Downloading {url}')
            _download(url, local_path)
        else:
            print(f'Reusing {local_path}')

        files.append({
            'month': month,
            'filename': filename,
            'source_url': url,
            'local_path': str(local_path),
            'compressed_bytes': local_path.stat().st_size,
        })

    return {
        'year': year,
        'work_dir': str(work_dir),
        'files': files,
    }


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output['files']) == 12, 'Expected one source file per month'
    assert all(Path(item['local_path']).exists() for item in output['files'])
