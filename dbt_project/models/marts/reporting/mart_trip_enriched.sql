with fact_dims_joined as (

    select

        trips.trip_id,

        trips.vendor_id,
        vendor.vendor_name,

        trips.service_type,
        trips.trip_type,
        trips.rate_code_id,

        trips.pickup_location_id,
        pickup_zone.borough as pickup_borough,
        pickup_zone.zone as pickup_zone,
        pickup_zone.service_zone as pickup_service_zone,

        trips.dropoff_location_id,
        dropoff_zone.borough as dropoff_borough,
        dropoff_zone.zone as dropoff_zone,
        dropoff_zone.service_zone as dropoff_service_zone,

        trips.payment_type_id,
        payment.payment_type_description,

        trips.pickup_datetime,
        trips.dropoff_datetime,
        trips.trip_duration_minutes,

        trips.passenger_count,
        trips.trip_distance,
        trips.fare_amount,
        trips.extra,
        trips.mta_tax,
        trips.tip_amount,
        trips.tolls_amount,
        trips.ehail_fee,
        trips.improvement_surcharge,
        trips.congestion_surcharge,
        trips.total_amount

    from {{ ref('fact_trip') }} as trips

    left join {{ ref('dim_vendor') }} as vendor
        on trips.vendor_id = vendor.vendor_id

    left join {{ ref('dim_zone') }} as pickup_zone
        on trips.pickup_location_id = pickup_zone.location_id

    left join {{ ref('dim_zone') }} as dropoff_zone
        on trips.dropoff_location_id = dropoff_zone.location_id

    left join {{ ref('dim_payment_type') }} as payment
        on trips.payment_type_id = payment.payment_type_id

)

select 

    trip_id,

    vendor_id,
    vendor_name,

    service_type,
    trip_type,
    rate_code_id,

    pickup_location_id,
    pickup_borough,
    pickup_zone,
    pickup_service_zone,

    dropoff_location_id,
    dropoff_borough,
    dropoff_zone,
    dropoff_service_zone,

    payment_type_id,
    payment_type_description,

    pickup_datetime,
    dropoff_datetime,
    trip_duration_minutes,

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

from fact_dims_joined
