select
    'internal_partner_value_gap' as check_name,
    valuation_date as observed_date,
    count_if(exceeds_tolerance) as affected_records,
    count(*) as total_records
from {{ ref('int_partner_reconciliation') }}
group by valuation_date

