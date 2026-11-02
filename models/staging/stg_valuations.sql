with source_data as (
    select     try_cast(account_id as varchar) as account_id,
    try_cast(valuation_date as date) as valuation_date,
    try_cast(total_value as number(18,2)) as total_value,
    try_cast(cash_value as number(18,2)) as cash_value,
    try_cast(currency as varchar) as currency,
    try_cast(updated_at as timestamp_tz) as updated_at,
    try_cast(loaded_at as timestamp_tz) as loaded_at
    from {{ source('wealthops_raw', 'raw_valuations') }}
),
ranked as (
    select *, row_number() over (
        partition by account_id, valuation_date order by updated_at desc nulls last, loaded_at desc nulls last
    ) as _row_rank
    from source_data
)
select * exclude (_row_rank) from ranked where _row_rank = 1
