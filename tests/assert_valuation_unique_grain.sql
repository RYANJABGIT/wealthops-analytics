select account_id, valuation_date
from {{ ref('fct_account_valuations_daily') }}
group by 1, 2 having count(*) > 1

