with source_data as (
    select     try_cast(account_id as varchar) as account_id,
    try_cast(customer_id as varchar) as customer_id,
    try_cast(product_type as varchar) as product_type,
    try_cast(opening_date as date) as opening_date,
    try_cast(closing_date as date) as closing_date,
    try_cast(account_status as varchar) as account_status,
    try_cast(partner_id as varchar) as partner_id,
    try_cast(updated_at as timestamp_tz) as updated_at,
    try_cast(loaded_at as timestamp_tz) as loaded_at
    from {{ source('wealthops_raw', 'raw_accounts') }}
),
ranked as (
    select *, row_number() over (
        partition by account_id order by updated_at desc nulls last, loaded_at desc nulls last
    ) as _row_rank
    from source_data
)
select * exclude (_row_rank) from ranked where _row_rank = 1
