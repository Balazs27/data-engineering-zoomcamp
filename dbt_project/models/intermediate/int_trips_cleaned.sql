-- Enrich and deduplicate trip data
-- Demonstrates enrichment and surrogate key generation
-- Note: Data quality analysis available in analyses/trips_data_quality.sql

with unioned as (
    
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
    
    from {{ ref('int_trips_unioned') }}

), cleaned_and_enriched as (


        select

            -- generate a unique trip identifier (surrogate key pattern)
            {{ dbt_utils.generate_surrogate_key([
                'service_type',
                'vendor_id',
                'pickup_datetime',
                'dropoff_datetime',
                'pickup_location_id',
                'dropoff_location_id',
                'passenger_count',
                'trip_distance',
                'fare_amount',
                'total_amount',
                'payment_type'
            ]) }} as trip_id,

            -- dimension keys
            vendor_id,
            rate_code_id,
            pickup_location_id,
            dropoff_location_id,
            coalesce(payment_type, 0) as payment_type_id,

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

        from unioned u

        /* DO NOT DEDUP IT UNTIL I CAN PROVE DUPLICATES!
        -- Deduplicate: if multiple trips match (same vendor, second, location, service), keep first
        qualify row_number() over(
        partition by vendor_id, pickup_datetime, pickup_location_id, service_type
        order by dropoff_datetime
        ) = 1 
        */

        /* This query retunrs 50 trip_id s with duplicate records, 1 with 45 the rest with 2:
        select
            trip_id,
            count(*) as row_count
        from `de-zoompcamp-learning.dbt_billovai.int_trips_cleaned`
        group by trip_id
        having count(*) > 1
        order by row_count desc
        */

)

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

from cleaned_and_enriched
