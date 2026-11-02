{{ config(
    materialized='incremental',
    unique_key=['account_id', 'valuation_date'],
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}
select account_id, product_type, valuation_date, total_value,
       cash_value, currency, updated_at
from {{ ref('int_daily_account_valuations') }}
{% if is_incremental() %}
where updated_at >= (
    select coalesce(dateadd(day, -2, max(updated_at)), '1900-01-01'::timestamp_tz)
    from {{ this }}
)
{% endif %}

