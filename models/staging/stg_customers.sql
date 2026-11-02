with source_data as (
    select     try_cast(customer_id as varchar) as customer_id,
    try_cast(registration_date as date) as registration_date,
    try_cast(country as varchar) as country,
    try_cast(customer_segment as varchar) as customer_segment,
    try_cast(customer_status as varchar) as customer_status,
    try_cast(updated_at as timestamp_tz) as updated_at,
    try_cast(loaded_at as timestamp_tz) as loaded_at
    from {{ source('wealthops_raw', 'raw_customers') }}
),
ranked as (
    select *, row_number() over (
        partition by customer_id order by updated_at desc nulls last, loaded_at desc nulls last
    ) as _row_rank
    from source_data
)
select * exclude (_row_rank) from ranked where _row_rank = 1
