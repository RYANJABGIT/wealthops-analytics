select
    p.partner_id, p.account_id, p.valuation_date,
    v.product_type, p.partner_value, v.total_value as internal_value,
    abs(p.partner_value - v.total_value) as absolute_difference,
    case when v.total_value > 0
         then abs(p.partner_value - v.total_value) / v.total_value
    end as relative_difference,
    (abs(p.partner_value - v.total_value) > 5) as exceeds_tolerance
from {{ ref('stg_partner_valuations') }} p
join {{ ref('int_daily_account_valuations') }} v
  on p.account_id = v.account_id
  and p.valuation_date = v.valuation_date
  and p.currency = v.currency
where p.currency = 'EUR'

