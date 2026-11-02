with source_data as (
    select     try_cast(fee_id as varchar) as fee_id,
    try_cast(account_id as varchar) as account_id,
    try_cast(fee_date as date) as fee_date,
    try_cast(fee_type as varchar) as fee_type,
    try_cast(fee_amount as number(18,2)) as fee_amount,
    try_cast(fee_status as varchar) as fee_status,
    try_cast(updated_at as timestamp_tz) as updated_at,
    try_cast(loaded_at as timestamp_tz) as loaded_at
    from {{ source('wealthops_raw', 'raw_fee_events') }}
),
ranked as (
    select *, row_number() over (
        partition by fee_id order by updated_at desc nulls last, loaded_at desc nulls last
    ) as _row_rank
    from source_data
)
select * exclude (_row_rank) from ranked where _row_rank = 1
