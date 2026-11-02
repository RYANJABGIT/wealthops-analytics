select v.account_id, a.product_type, v.valuation_date, v.total_value,
       v.cash_value, v.currency, v.updated_at
from {{ ref('stg_valuations') }} v
join {{ ref('stg_accounts') }} a on v.account_id = a.account_id
where v.currency = 'EUR' and v.total_value >= 0
  and v.cash_value >= 0 and v.cash_value <= v.total_value

