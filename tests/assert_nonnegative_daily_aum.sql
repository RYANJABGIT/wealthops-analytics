select * from {{ ref('mart_daily_aum') }} where aum_eur < 0

