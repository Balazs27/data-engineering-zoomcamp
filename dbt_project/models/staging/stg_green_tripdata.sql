with staging as (

    select

        -- identifiers
        VendorID as vendor_id,
        RatecodeID as rate_code_id,
        PULocationID as pickup_location_id,
        DOLocationID dropoff_location_id,

        -- timestamps
        lpep_pickup_datetime as pickup_datetime,		
        lpep_dropoff_datetime as dropoff_datetime,

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
        improvement_surcharge,
        total_amount,
        payment_type,
        congestion_surcharge

    from {{ source('raw_data', 'green_tripdata_partitioned') }}

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
    improvement_surcharge,
    total_amount,
    payment_type,
    congestion_surcharge

from staging
		