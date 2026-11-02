-- WealthOps Analytics: rapid Snowflake-native DEMO seed.
-- Uses synthetic generated data only; does NOT require a local Python installation.
-- WARNING: Replaces only the six WEALTHOPS_DB.RAW.RAW_* demo tables.
-- If you previously loaded CSV data into these tables, do not run this script.
USE ROLE SYSADMIN;
USE WAREHOUSE WEALTHOPS_WH;
USE DATABASE WEALTHOPS_DB;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE RAW_CUSTOMERS AS
WITH ids AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 60))
)
SELECT
  'C' || LPAD(TO_VARCHAR(n + 1), 6, '0') AS customer_id,
  DATEADD(day, -MOD(n, 120), '2026-09-01'::DATE)::DATE AS registration_date,
  'FR' AS country,
  IFF(MOD(n, 5) = 0, 'AFFLUENT', 'MASS') AS customer_segment,
  'ACTIVE' AS customer_status,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM ids;

CREATE OR REPLACE TABLE RAW_ACCOUNTS AS
WITH ids AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 90))
)
SELECT
  'A' || LPAD(TO_VARCHAR(n + 1), 7, '0') AS account_id,
  'C' || LPAD(TO_VARCHAR(MOD(n, 60) + 1), 6, '0') AS customer_id,
  CASE MOD(n, 3) WHEN 0 THEN 'ASSURANCE_VIE' WHEN 1 THEN 'PEA' ELSE 'PER' END AS product_type,
  DATEADD(day, MOD(n, 20), '2026-08-01'::DATE)::DATE AS opening_date,
  NULL::DATE AS closing_date,
  'OPEN' AS account_status,
  'P-0' || TO_VARCHAR(MOD(n, 4) + 1) AS partner_id,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM ids;

CREATE OR REPLACE TABLE RAW_TRANSACTIONS AS
WITH ids AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 400))
)
SELECT
  'T' || LPAD(TO_VARCHAR(n + 1), 9, '0') AS transaction_id,
  'A' || LPAD(TO_VARCHAR(MOD(n, 90) + 1), 7, '0') AS account_id,
  CASE
    WHEN MOD(n, 10) < 5 THEN 'deposit'
    WHEN MOD(n, 10) < 8 THEN 'withdrawal'
    WHEN MOD(n, 10) = 8 THEN 'internal_transfer_in'
    ELSE 'internal_transfer_out'
  END AS transaction_type,
  (100 + MOD(n * 67, 9000))::NUMBER(18,2) AS transaction_amount,
  'EUR' AS currency,
  DATEADD(day, MOD(n, 30), '2026-10-01'::DATE)::DATE AS transaction_date,
  CASE
    WHEN MOD(n, 19) = 0 THEN 'pending'
    WHEN MOD(n, 19) = 1 THEN 'rejected'
    WHEN MOD(n, 19) = 2 THEN 'cancelled'
    ELSE 'completed'
  END AS transaction_status,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM ids;

CREATE OR REPLACE TABLE RAW_VALUATIONS AS
WITH account_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 90))
), day_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS d
  FROM TABLE(GENERATOR(ROWCOUNT => 30))
)
SELECT
  'A' || LPAD(TO_VARCHAR(a.n + 1), 7, '0') AS account_id,
  DATEADD(day, d.d, '2026-10-01'::DATE)::DATE AS valuation_date,
  (5000 + a.n * 75 + d.d * 10)::NUMBER(18,2) AS total_value,
  (200 + MOD(a.n * 12, 500))::NUMBER(18,2) AS cash_value,
  'EUR' AS currency,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM account_indices a CROSS JOIN day_indices d;

CREATE OR REPLACE TABLE RAW_FEE_EVENTS AS
WITH account_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 90))
), fee_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS f
  FROM TABLE(GENERATOR(ROWCOUNT => 2))
)
SELECT
  'F' || LPAD(TO_VARCHAR(a.n * 2 + f.f + 1), 9, '0') AS fee_id,
  'A' || LPAD(TO_VARCHAR(a.n + 1), 7, '0') AS account_id,
  DATEADD(day, 10 + f.f * 15, '2026-10-01'::DATE)::DATE AS fee_date,
  'management' AS fee_type,
  (3 + MOD(a.n, 12))::NUMBER(18,2) AS fee_amount,
  'posted' AS fee_status,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM account_indices a CROSS JOIN fee_indices f;

CREATE OR REPLACE TABLE RAW_PARTNER_VALUATIONS AS
WITH account_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS n
  FROM TABLE(GENERATOR(ROWCOUNT => 90))
), week_indices AS (
  SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS w
  FROM TABLE(GENERATOR(ROWCOUNT => 5))
)
SELECT
  'P-0' || TO_VARCHAR(MOD(a.n, 4) + 1) AS partner_id,
  'A' || LPAD(TO_VARCHAR(a.n + 1), 7, '0') AS account_id,
  DATEADD(day, w.w * 7, '2026-10-01'::DATE)::DATE AS valuation_date,
  (5000 + a.n * 75 + w.w * 70 + IFF(MOD(a.n, 11) = 0, 12, 0))::NUMBER(18,2) AS partner_value,
  'EUR' AS currency,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS updated_at,
  CURRENT_TIMESTAMP()::TIMESTAMP_TZ AS loaded_at
FROM account_indices a CROSS JOIN week_indices w;

-- Expected row counts: 60, 90, 400, 2700, 180, 450.
SELECT 'RAW_CUSTOMERS' AS source_table, COUNT(*) AS rows_loaded FROM RAW_CUSTOMERS
UNION ALL SELECT 'RAW_ACCOUNTS', COUNT(*) FROM RAW_ACCOUNTS
UNION ALL SELECT 'RAW_TRANSACTIONS', COUNT(*) FROM RAW_TRANSACTIONS
UNION ALL SELECT 'RAW_VALUATIONS', COUNT(*) FROM RAW_VALUATIONS
UNION ALL SELECT 'RAW_FEE_EVENTS', COUNT(*) FROM RAW_FEE_EVENTS
UNION ALL SELECT 'RAW_PARTNER_VALUATIONS', COUNT(*) FROM RAW_PARTNER_VALUATIONS
ORDER BY source_table;
