select valuation_date, product_type, sum(total_value) as aum_eur,
       count(distinct account_id) as active_valued_accounts
from {{ ref('fct_account_valuations_daily') }}
group by 1, 2

