select
    date_trunc('month', transaction_date)::date as cashflow_month,
    product_type,
    sum(case when transaction_type = 'deposit' then transaction_amount else 0 end) as gross_inflows_eur,
    sum(case when transaction_type = 'withdrawal' then transaction_amount else 0 end) as gross_outflows_eur,
    sum(net_external_cashflow) as net_inflows_eur
from {{ ref('int_completed_cashflows') }}
group by 1, 2

