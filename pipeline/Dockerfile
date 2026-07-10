# base Docker image that we will build on
FROM python:3.13.11-slim

# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# set up our image by installing prerequisites; pandas and pyarrow in this case
#RUN pip install pandas pyarrow

# Set working directory
WORKDIR /app

# Add virtual environment to PATH so we can use installed packages
#ENV PATH="/app/.venv/bin:$PATH" # then we do not need ENTRYPOINT ["uv", "run", ...]

# Copy dependency files first (better layer caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked

# Copy ingestion scripts to the container
COPY ingest_data_cli.py .
COPY ingest_lookup_cli.py .
COPY ingest_data_2021_cli.py .

# Run Python through uv.
# The actual script name will be provided in docker compose run.
ENTRYPOINT ["uv", "run", "python"]