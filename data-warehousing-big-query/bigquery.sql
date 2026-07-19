--MODULE 3 - DATA WAREHOUSING - BIGQUERY - COST AND PERFORMANCE OPTIMIZATION

--WARNING: The CREATE OR REPLACE statements below modify BigQuery resources,
--and running these queries can incur Google Cloud charges. Review the project,
--dataset, table, and GCS identifiers before executing this file.

--CREATING AND EXTERNAL TABLE THAT REFERS TO THE DATA INSIDE MY GCS BUCKET
CREATE OR REPLACE EXTERNAL TABLE `de-zoompcamp-learning.demo_dataset.external_yellow_tripdata`
  OPTIONS (
    format = 'CSV',
    uris = ['gs://de-zoompcamp-learning-terraform-bucket/nyc_taxi_trips_2019/yellow_tripdata_2019-*.csv'],
    skip_leading_rows = 1
  );

--QUERY MY TABLE
SELECT * FROM de-zoompcamp-learning.demo_dataset.external_yellow_tripdata LIMIT 10;

--CREATING NON-PARTITIONED TABLE
CREATE OR REPLACE TABLE `de-zoompcamp-learning.demo_dataset.yellow_tripdata_non_partitioned` AS
SELECT * FROM `de-zoompcamp-learning.demo_dataset.external_yellow_tripdata`;

--CREATING PARTITIONED TABLE
CREATE OR REPLACE TABLE `de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned`
PARTITION BY DATE(tpep_pickup_datetime) AS
SELECT * FROM `de-zoompcamp-learning.demo_dataset.external_yellow_tripdata`;

--CREATING PARTITIONED AND CLUSTERED TABLE
CREATE OR REPLACE TABLE `de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM `de-zoompcamp-learning.demo_dataset.external_yellow_tripdata`;

--IMPACT OF PARTITION
--Scanning 1.23GB of data
SELECT DISTINCT(VendorID)
FROM de-zoompcamp-learning.demo_dataset.yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

--Scanning ~104 MB of data
SELECT DISTINCT(VendorID)
FROM de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

--Inspect table partitions
SELECT
    table_name,
    partition_id,
    total_rows
FROM `demo_dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC;


--PARTITIONED VS PARTITIONED AND CLUSTERED TABLE
--Query scans ~700 MB of data
SELECT count(*) as trips
FROM de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
AND VendorID=1;

--Query scans 516 MB of data
SELECT count(*) as trips
FROM de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
AND VendorID=1;

--PARTITIONED VS PARTITIONED AND CLUSTERED TABLE PART 2
--Query scans 156 MB of data
SELECT
    VendorID,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS total_revenue
FROM `de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned`
WHERE tpep_pickup_datetime >= TIMESTAMP('2019-06-01')
    AND tpep_pickup_datetime < TIMESTAMP('2019-07-01')
    AND VendorID = 2
GROUP BY VendorID;

--Query scans 134 MB of data
SELECT
    VendorID,
    COUNT(*) AS trip_count,
    SUM(total_amount) AS total_revenue
FROM `de-zoompcamp-learning.demo_dataset.yellow_tripdata_partitioned_clustered`
WHERE tpep_pickup_datetime >= TIMESTAMP('2019-06-01')
    AND tpep_pickup_datetime < TIMESTAMP('2019-07-01')
    AND VendorID = 2
GROUP BY VendorID;
