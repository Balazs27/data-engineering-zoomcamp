/*
To Do:
- One row per trip (doesn't matter if yellow or green)
- Add a primary key (trip_id). It has to be unique.
- Find all the duplicates, understand why they happen, and fix them.
- Find a way to enrich the column payment_type.
*/

with int_trips_cleaned as (

    select 
    
        -- row indentifier
        trip_id,
        
        -- dimension keys
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        payment_type_id,

        -- event timestamps
        pickup_datetime,
        dropoff_datetime,

        -- descriptive trip attributes
        service_type,
        store_and_fwd_flag,
        trip_type,

        -- facts
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        ehail_fee,
        improvement_surcharge,
        congestion_surcharge,
        total_amount 
    
    from {{ ref('int_trips_cleaned') }}
)

select

    -- fact row identifier
    trip_id,

    -- dimension foreign keys / codes
    vendor_id,
    payment_type_id,
    pickup_location_id,
    dropoff_location_id,
    rate_code_id,

    -- degenerate / low-cardinality attributes
    service_type,
    store_and_fwd_flag,
    trip_type,

    -- event timestamps
    pickup_datetime,
    dropoff_datetime,

    -- derived facts
    {{ get_trip_duration_minutes('pickup_datetime', 'dropoff_datetime') }} as trip_duration_minutes,

    -- additive and semi-additive facts
    passenger_count,
    trip_distance,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    ehail_fee,
    improvement_surcharge,
    congestion_surcharge,
    total_amount

from int_trips_cleaned