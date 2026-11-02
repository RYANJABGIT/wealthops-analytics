select
    t.transaction_id,
    t.account_id,
    a.product_type,
    t.transaction_date,
    t.transaction_type,
    t.transaction_amount,
    case
        when t.transaction_type = 'deposit' then t.transaction_amount
        when t.transaction_type = 'withdrawal' then -t.transaction_amount
        else cast(0 as number(18,2))
    end as net_external_cashflow
from {{ ref('stg_transactions') }} t
join {{ ref('stg_accounts') }} a on t.account_id = a.account_id
where t.transaction_status = 'completed'
  and t.currency = 'EUR'
  and t.transaction_amount > 0

