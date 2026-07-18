with int_trips as (

    select 

        -- identifiers
        trip_id, --surrogate_key
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

    from {{ ref('int_trips_cleaned') }}

), vendors as (

   select
    
        distinct vendor_id,
        {{ get_vendor_name('vendor_id') }} as vendor_name

    from int_trips

)

select

    vendor_id,
    vendor_name

from vendors