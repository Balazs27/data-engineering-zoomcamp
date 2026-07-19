with green_taxi_source as (

    select

        -- identifiers
        cast(VendorID as integer) as vendor_id,
        cast(RatecodeID as integer) as rate_code_id,
        cast(PULocationID as integer) as pickup_location_id,
        cast(DOLocationID as integer) as dropoff_location_id,

        -- timestamps
        cast(lpep_pickup_datetime as timestamp) as pickup_datetime,		
        cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,

        --trip info
        cast(store_and_fwd_flag as string) as store_and_fwd_flag,
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as numeric) as trip_distance,
        cast(trip_type as integer) as trip_type,

        -- paymeny info
        cast(fare_amount as numeric) as fare_amount,
        cast(extra as numeric) as extra,
        cast(mta_tax as numeric) as mta_tax,
        cast(tip_amount as numeric) as tip_amount,
        cast(tolls_amount as numeric) as tolls_amount,
        cast(ehail_fee as numeric) as ehail_fee,
        cast(improvement_surcharge as numeric) as improvement_surcharge,
        cast(congestion_surcharge as numeric) as congestion_surcharge,
        cast(total_amount as numeric) as total_amount,
        cast(payment_type as integer) as payment_type

    from {{ source('raw_data', 'green_tripdata_partitioned') }}
    -- Sample records for dev environment using deterministic date filter
    {% if target.name == 'dev' and var('limit_dev_data', true) %}
    where pickup_datetime >= timestamp('{{ var("dev_start_date") }}')
      and pickup_datetime < timestamp('{{ var("dev_end_date") }}')
    {% endif %}

)

select

    -- identifiers
    vendor_id,
    rate_code_id,
    pickup_location_id,
    dropoff_location_id,

    -- timestamps
    pickup_datetime,		
    dropoff_datetime,

    --trip info
    store_and_fwd_flag,
    passenger_count,
    trip_distance,
    trip_type,

    -- paymeny info
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    ehail_fee,
    improvement_surcharge,
    congestion_surcharge,
    total_amount,
    payment_type
    
from green_taxi_source
		