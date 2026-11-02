select
    account_id, date_trunc('month', fee_date)::date as fee_month,
    sum(fee_amount) as booked_fee_amount
from {{ ref('stg_fee_events') }}
where fee_status = 'posted' and fee_amount >= 0
group by 1, 2

