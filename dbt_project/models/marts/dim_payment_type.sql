with payment_types as (

    select

        cast(payment_type as integer) as payment_type_id,
        description as payment_type_description

    from {{ ref('payment_type_lookup') }}

)

select

    payment_type_id,
    payment_type_description
    
from payment_types