{% snapshot snap_accounts %}
{{
    config(
      target_schema='AUDIT',
      unique_key='account_id',
      strategy='timestamp',
      updated_at='updated_at',
      invalidate_hard_deletes=False
    )
}}
select account_id, customer_id, product_type, opening_date, closing_date,
       account_status, partner_id, updated_at
from {{ ref('stg_accounts') }}
{% endsnapshot %}

