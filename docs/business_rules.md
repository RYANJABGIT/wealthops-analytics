# Business definitions (synthetic fintech)

All amounts are EUR decimal numbers with 2 decimal places. No actual customer data.

- **Grain:** transactions are one row per transaction ID; account valuations are one row per account and valuation date.
- **Gross inflows:** completed external deposits only.
- **Gross outflows:** completed external withdrawals (positive amount).
- **Net inflows:** gross inflows minus gross outflows. Internal transfers do not change firm-wide net inflows.
- **AUM:** total account valuation (including cash) on a given date; semi-additive: sum across accounts at the same date, never across dates.
- **Fees:** only posted fee events count as booked fees. They do not imply net revenue.
- **Reconciliation:** absolute difference between same-day, same-account, same-currency internal and partner valuations. Example tolerance EUR 5, configurable in SQL.
- **Dates:** transaction_date and valuation_date describe business events; loaded_at describes technical arrival time.
- **Demonstration limitation:** synthetic daily valuations are generated independently from simulated cashflows; this is NOT a realistic investment performance model and should not be used for accounting or trading.

