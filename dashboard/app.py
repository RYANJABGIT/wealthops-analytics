"""Streamlit BI consuming modeled Snowflake marts (no hard-coded KPIs)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.load_snowflake import connect  # noqa: E402

st.set_page_config(page_title="WealthOps Analytics", layout="wide")
st.title("WealthOps | Analytics")
st.caption("Synthetic finance data only • Snowflake + dbt portfolio")

if not (os.environ.get("SNOWFLAKE_ACCOUNT") or Path(".env").exists()):
    st.info("Configure a Snowflake Trial account and local .env before starting the dashboard.")
    st.stop()


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetch_pandas_all()


try:
    max_date = query("select max(VALUATION_DATE) as MAX_DATE from WEALTHOPS_DB.MARTS.MART_DAILY_AUM")
    latest = max_date["MAX_DATE"].iloc[0]
    if pd.isna(latest):
        st.warning("No modeled valuations available. Run dbt build.")
        st.stop()
    financial, transactions, quality = st.tabs(["Financial overview", "Cash flows", "Data quality"])
    with financial:
        st.metric("Latest valuation date", str(latest)[:10])
        kpi = query(
            "select PRODUCT_TYPE, sum(AUM_EUR) as AUM_EUR "
            "from WEALTHOPS_DB.MARTS.MART_DAILY_AUM "
            f"where VALUATION_DATE = '{latest:%Y-%m-%d}' group by 1"
        )
        st.metric("Assets under management (EUR)", f"{kpi['AUM_EUR'].sum():,.2f}")
        st.dataframe(kpi, use_container_width=True)
        aum = query(
            "select VALUATION_DATE, PRODUCT_TYPE, AUM_EUR "
            "from WEALTHOPS_DB.MARTS.MART_DAILY_AUM order by 1"
        )
        pivot = aum.pivot(index="VALUATION_DATE", columns="PRODUCT_TYPE", values="AUM_EUR")
        st.line_chart(pivot)
    with transactions:
        monthly = query(
            "select CASHFLOW_MONTH, PRODUCT_TYPE, GROSS_INFLOWS_EUR, "
            "GROSS_OUTFLOWS_EUR, NET_INFLOWS_EUR "
            "from WEALTHOPS_DB.MARTS.MART_MONTHLY_CASHFLOWS "
            "order by CASHFLOW_MONTH desc"
        )
        st.dataframe(monthly, use_container_width=True)
        st.bar_chart(monthly.groupby("CASHFLOW_MONTH")["NET_INFLOWS_EUR"].sum())
    with quality:
        q = query(
            "select CHECK_NAME, OBSERVED_DATE, AFFECTED_RECORDS, TOTAL_RECORDS "
            "from WEALTHOPS_DB.MARTS.MART_DATA_QUALITY "
            "order by OBSERVED_DATE desc"
        )
        st.dataframe(q, use_container_width=True)
        recon = query(
            "select PARTNER_ID, VALUATION_DATE, ANOMALY_COUNT, "
            "SUM_ABSOLUTE_DIFFERENCE_EUR "
            "from WEALTHOPS_DB.MARTS.MART_PARTNER_RECONCILIATION "
            "where ANOMALY_COUNT > 0 order by VALUATION_DATE desc limit 100"
        )
        st.subheader("Partner discrepancies")
        st.dataframe(recon, use_container_width=True)
except Exception as exc:
    st.error("Could not query Snowflake marts. Check credentials, roles and dbt build.")
    st.code(str(exc))

