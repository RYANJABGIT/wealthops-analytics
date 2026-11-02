with source_data as (
    select     try_cast(transaction_id as varchar) as transaction_id,
    try_cast(account_id as varchar) as account_id,
    try_cast(transaction_type as varchar) as transaction_type,
    try_cast(transaction_amount as number(18,2)) as transaction_amount,
    try_cast(currency as varchar) as currency,
    try_cast(transaction_date as date) as transaction_date,
    try_cast(transaction_status as varchar) as transaction_status,
    try_cast(updated_at as timestamp_tz) as updated_at,
    try_cast(loaded_at as timestamp_tz) as loaded_at
    from {{ source('wealthops_raw', 'raw_transactions') }}
),
ranked as (
    select *, row_number() over (
        partition by transaction_id order by updated_at desc nulls last, loaded_at desc nulls last
    ) as _row_rank
    from source_data
)
select * exclude (_row_rank) from ranked where _row_rank = 1
