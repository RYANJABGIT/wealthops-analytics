select partner_id, valuation_date, product_type,
       count(*) as compared_accounts,
       sum(case when exceeds_tolerance then 1 else 0 end) as anomaly_count,
       sum(absolute_difference) as sum_absolute_difference_eur
from {{ ref('int_partner_reconciliation') }}
group by 1, 2, 3

