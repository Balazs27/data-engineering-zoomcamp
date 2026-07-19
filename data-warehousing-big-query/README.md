# GCS to BigQuery: External Tables, Partitioning, and Clustering

## Module goal

In this module, I explored how data stored in Google Cloud Storage (GCS) can
be queried and materialized in BigQuery. I then compared a regular BigQuery
table with partitioned and clustered versions of the same data to understand
how table design affects query performance and cost.

The main lesson was that BigQuery does not always need to scan an entire table.
When queries filter on well-chosen partitioning and clustering columns,
BigQuery can skip data that cannot match the query.

## Data flow

The input was the 2019 NYC yellow taxi trip dataset, with one CSV file for each
month. A Mage pipeline downloaded and cleaned the source data and uploaded the
12 resulting files into one shared folder in my GCS bucket:

```text
gs://de-zoompcamp-learning-terraform-bucket/
└── nyc_taxi_trips_2019/
    ├── yellow_tripdata_2019-01.csv
    ├── yellow_tripdata_2019-02.csv
    ├── ...
    └── yellow_tripdata_2019-12.csv
```

Both the GCS bucket and BigQuery dataset are in the `EU` location. The
Terraform-managed BigQuery dataset is named `demo_dataset`.

## Creating an external table over the GCS files

I first created an external table using a wildcard URI:

```sql
CREATE OR REPLACE EXTERNAL TABLE
  `de-zoompcamp-learning.demo_dataset.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://de-zoompcamp-learning-terraform-bucket/nyc_taxi_trips_2019/yellow_tripdata_2019-*.csv'
  ],
  skip_leading_rows = 1
);
```

The wildcard makes the 12 monthly files appear as one table. The external
table stores the table definition and schema in BigQuery, but the trip data
continues to live in GCS. Queries read the source files from GCS at execution
time.

This explains why the external table's Details page does not show the same
managed storage size and row-count information as a native BigQuery table.
BigQuery does not own the underlying storage or maintain the same table storage
statistics for external tables. External tables are useful for querying data
without loading it first, although they can be slower than native BigQuery
tables. See [Introduction to external tables](https://docs.cloud.google.com/bigquery/docs/external-tables).

## Creating native BigQuery tables

I materialized the external data into three native BigQuery tables:

| Table | Storage design | Purpose |
| --- | --- | --- |
| `yellow_tripdata_non_partitioned` | No partitioning or clustering | Baseline for comparison |
| `yellow_tripdata_partitioned` | Partitioned by `DATE(tpep_pickup_datetime)` | Allows BigQuery to skip dates outside the query range |
| `yellow_tripdata_partitioned_clustered` | Partitioned by pickup date and clustered by `VendorID` | Also groups similar vendor values within each partition |

Unlike the external table, these tables are stored and managed by BigQuery.
Their Details pages show information such as row count and storage size. For
the optimized tables, BigQuery also displays the partitioning and clustering
columns.

## Results from my queries

### Effect of partitioning

I selected distinct vendors for June 2019 from the non-partitioned and
partitioned tables:

| Table | Data scanned |
| --- | ---: |
| Non-partitioned | 1.23 GB |
| Partitioned | approximately 104 MB |

The partitioned query scanned roughly 92% less data. BigQuery only needed the
June partitions instead of reading the full year. This is called **partition
pruning**: partitions that cannot satisfy the date filter are excluded from
the scan and from the bytes processed. See [Query partitioned tables](https://docs.cloud.google.com/bigquery/docs/querying-partitioned-tables).

### Additional effect of clustering

I then filtered by both a pickup-date range and `VendorID`:

| Query | Partitioned | Partitioned and clustered |
| --- | ---: | ---: |
| Broad date range, `VendorID = 1` | approximately 700 MB | 516 MB |
| June 2019, `VendorID = 2` | 156 MB | 134 MB |

Clustering reduced the scans by approximately 26% and 14%, respectively. The
improvement was smaller than the partitioning improvement, which makes sense
for this experiment:

- Partitioning eliminated most of the year using the date range.
- `VendorID` has very few distinct values, so it is not an ideal high-cardinality
  clustering column.
- The table is relatively small, so many storage blocks cannot be eliminated.

Clustering can also make the pre-run byte estimate less exact because BigQuery
determines which storage blocks can be pruned during query execution. The
completed job's actual bytes processed are therefore important when evaluating
clustering.

## Partitioning versus clustering

| Partitioning | Clustering |
| --- | --- |
| Divides a table into separate partitions | Sorts and organizes storage blocks by column values |
| Usually based on a `DATE`, `TIMESTAMP`, `DATETIME`, ingestion time, or integer range | Supports up to four eligible top-level columns |
| Best when queries commonly restrict a clear range, especially time | Best when queries frequently filter on specific values or ranges |
| Eliminates complete partitions | Eliminates blocks within a table or partition |
| Gives more predictable pre-run cost estimates | Exact savings might only be known after execution |
| Too many small partitions create unnecessary metadata | BigQuery maintains clustering as data changes |

They are complementary rather than competing features. Partitioning first
removes irrelevant partitions, and clustering can then remove irrelevant
blocks inside the remaining partitions.

## Choosing a partitioning column

A good partitioning column should:

- appear frequently in query filters;
- divide data into useful, reasonably sized ranges;
- usually represent event time, creation time, business date, or another
  natural lifecycle boundary;
- match how data is retained or deleted, because partitions can have separate
  expiration policies.

Typical examples include `event_date`, `created_at`, `transaction_timestamp`,
and, in this dataset, `tpep_pickup_datetime`.

Avoid partitioning on a column simply because it appears in the schema. A
customer or trip ID usually creates too many tiny ranges and is generally a
better clustering candidate. The partition granularity should also match the
data volume: daily partitions are common, while hourly partitions are mainly
useful for very high-volume data over relatively short time ranges.

Google recommends considering whether partitioning produces average partitions
of at least approximately **10 GB** when combining partitioning and clustering.
Many tiny partitions add metadata overhead. This is a guideline rather than a
hard minimum: smaller tables can still demonstrate partition pruning, as this
experiment did. See [Introduction to clustered tables](https://docs.cloud.google.com/bigquery/docs/clustered-tables).

For reliable pruning, queries should directly restrict the partitioning column
with a constant range. A half-open range avoids overlap at the boundary:

```sql
WHERE tpep_pickup_datetime >= TIMESTAMP('2019-06-01')
  AND tpep_pickup_datetime < TIMESTAMP('2019-07-01')
```

For important production tables, `require_partition_filter = TRUE` can prevent
users from accidentally submitting queries that scan every partition.

## Choosing clustering columns

A good clustering column should:

- appear frequently in `WHERE` filters;
- have enough distinct values to let BigQuery eliminate meaningful groups of
  storage blocks;
- be used in common range filters or aggregations;
- come first in the clustering order if it is the most commonly filtered
  clustering column.

Examples include `customer_id`, `account_id`, `country`, `status`, or product
identifiers, depending on the workload. For this taxi dataset,
`PULocationID` or `DOLocationID` could be useful alternatives if queries often
filter trips by location. `VendorID` is still useful for learning, but its low
cardinality limits how much data BigQuery can skip.

Google states that unpartitioned tables larger than approximately **64 MB** are
likely to benefit from clustering. For partitioned tables, individual
partitions larger than approximately **64 MB** are more likely to benefit.
Below that size, clustering is allowed, but the improvement is often
negligible. Column choice and real query patterns remain more important than a
single size threshold. See [Introduction to clustered tables](https://docs.cloud.google.com/bigquery/docs/clustered-tables).

When using multiple clustering columns, their order matters. BigQuery sorts by
the first column, then the second, and so on. Filters beginning with the first
clustering column generally enable the most effective block pruning. See
[Querying clustered tables](https://docs.cloud.google.com/bigquery/docs/querying-clustered-tables).

## Main takeaways

1. An external table lets BigQuery query files in GCS without moving the data
   into BigQuery-managed storage.
2. An external table does not expose the same native storage and row-count
   statistics because the underlying data remains outside BigQuery.
3. Materializing the data as a native table provides BigQuery-managed storage,
   metadata, and more optimization options.
4. Partitioning provides the largest benefit when queries consistently filter
   on the partitioning column.
5. Clustering provides an additional benefit when queries filter on useful
   clustering columns and the remaining partitions or table are large enough.
6. Optimization should be evaluated using actual query patterns and bytes
   processed, not only elapsed time on one query.
7. For this experiment, date partitioning produced the clearest saving, while
   clustering by low-cardinality `VendorID` produced a smaller but measurable
   additional reduction.

The SQL used to create the tables and record the query comparisons is in
[`bigquery.sql`](./bigquery.sql).
