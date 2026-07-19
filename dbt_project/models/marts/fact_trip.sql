--Fact table with dimension keys, additive, semi-additive facts and derived facts

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