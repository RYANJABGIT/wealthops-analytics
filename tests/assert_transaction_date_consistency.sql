select t.transaction_id
from {{ ref('fct_transactions') }} t
join {{ ref('dim_accounts') }} a on t.account_id = a.account_id
where t.transaction_date < a.opening_date
   or (a.closing_date is not null and t.transaction_date > a.closing_date)

