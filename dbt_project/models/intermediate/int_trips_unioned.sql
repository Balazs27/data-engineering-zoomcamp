-- Union green and yellow taxi data into a single dataset
-- Demonstrates how to combine data from multiple sources with slightly different schemas

with green_staging as (

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
        payment_type,
        'green' as service_type
    
    from {{ ref('stg_green_tripdata') }}
    -- Filter out records with null vendor_id (data quality requirement)
    where vendor_id is not null

), yellow_staging as (

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
        cast(1 as integer) as trip_type,

        -- paymeny info
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        cast(0 as numeric) as ehail_fee,
        improvement_surcharge,
        congestion_surcharge,
        total_amount,
        payment_type,
        'yellow' as service_type
    
    from {{ ref('stg_yellow_tripdata') }}
    -- Filter out records with null vendor_id (data quality requirement)
    where vendor_id is not null

), unioned as (

    select * from green_staging

    union all

    select * from yellow_staging

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
    payment_type,
    service_type

from unioned