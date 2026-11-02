# Architecture

```mermaid
flowchart TD
 G[Python deterministic generator] --> CSV[Synthetic CSV files]
 CSV --> RAW[Snowflake RAW tables]
 RAW --> STG[dbt staging views]
 STG --> INT[dbt intermediate views]
 INT --> MARTS[dbt dimensional marts]
 MARTS --> BI[Streamlit financial dashboards]
 RAW --> DQ[Source tests & freshness]
 MARTS --> DQ2[dbt data tests]
```

## Decisions
- Snowflake + dbt Core resemble a real modern analytics-engineering stack, suitable for a personal trial account.
- RAW source reset on demo load is intentional. No claims of production ingestion robustness.
- Staging models normalize fields; intermediate models encode rules; marts expose dimensions, facts and KPIs.
- Development warehouse is X-SMALL with 60-second auto-suspend.
- All data are generated, not collected from any fintech or exchange.
- Do not use this dashboard to make investment decisions.

## Security
Credentials are environment variables or local ~/.dbt/profiles.yml; never commit them. GitHub CI performs offline checks unless separate integration secrets are supplied.

