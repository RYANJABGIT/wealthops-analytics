select * from {{ ref('mart_monthly_cashflows') }}
where abs(net_inflows_eur - (gross_inflows_eur - gross_outflows_eur)) > 0.01

