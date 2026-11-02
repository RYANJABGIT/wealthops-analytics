"""Load synthetic CSV files into pre-created Snowflake RAW tables.

Bootstrap once using sql/bootstrap.sql in a Snowflake worksheet. Each demo load
replaces the synthetic RAW table; production-style ingestion is out of scope.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from scripts.generate_data import HEADERS

DDL = {
    "raw_customers": "CUSTOMER_ID VARCHAR, REGISTRATION_DATE DATE, COUNTRY VARCHAR, CUSTOMER_SEGMENT VARCHAR, CUSTOMER_STATUS VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
    "raw_accounts": "ACCOUNT_ID VARCHAR, CUSTOMER_ID VARCHAR, PRODUCT_TYPE VARCHAR, OPENING_DATE DATE, CLOSING_DATE DATE, ACCOUNT_STATUS VARCHAR, PARTNER_ID VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
    "raw_transactions": "TRANSACTION_ID VARCHAR, ACCOUNT_ID VARCHAR, TRANSACTION_TYPE VARCHAR, TRANSACTION_AMOUNT NUMBER(18,2), CURRENCY VARCHAR, TRANSACTION_DATE DATE, TRANSACTION_STATUS VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
    "raw_valuations": "ACCOUNT_ID VARCHAR, VALUATION_DATE DATE, TOTAL_VALUE NUMBER(18,2), CASH_VALUE NUMBER(18,2), CURRENCY VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
    "raw_fee_events": "FEE_ID VARCHAR, ACCOUNT_ID VARCHAR, FEE_DATE DATE, FEE_TYPE VARCHAR, FEE_AMOUNT NUMBER(18,2), FEE_STATUS VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
    "raw_partner_valuations": "PARTNER_ID VARCHAR, ACCOUNT_ID VARCHAR, VALUATION_DATE DATE, PARTNER_VALUE NUMBER(18,2), CURRENCY VARCHAR, UPDATED_AT TIMESTAMP_TZ, LOADED_AT TIMESTAMP_TZ",
}


def connect():
    from dotenv import load_dotenv
    import snowflake.connector

    load_dotenv()
    kwargs = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "WEALTHOPS_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "WEALTHOPS_DB"),
        "role": os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
        "authenticator": os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
    }
    if os.getenv("SNOWFLAKE_PASSWORD"):
        kwargs["password"] = os.getenv("SNOWFLAKE_PASSWORD")
    return snowflake.connector.connect(**kwargs)


def load(directory: Path) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("USE SCHEMA RAW")
            for name, columns in DDL.items():
                table = name.upper()
                file = (directory / f"{name}.csv").resolve()
                if not file.is_file():
                    raise FileNotFoundError(file)
                with file.open(encoding="utf-8", newline="") as inp:
                    if next(csv.reader(inp)) != HEADERS[name]:
                        raise ValueError(f"Unexpected header in {file}")
                cur.execute(f"CREATE OR REPLACE TABLE {table} ({columns})")
                cur.execute(
                    f"PUT 'file://{file.as_posix()}' @%{table} "
                    "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
                )
                cur.execute(
                    f"COPY INTO {table} FROM @%{table} "
                    "FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1 "
                    "FIELD_OPTIONALLY_ENCLOSED_BY='\"' NULL_IF=('','NULL')) "
                    "ON_ERROR=ABORT_STATEMENT PURGE=TRUE"
                )
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table}: {cur.fetchone()[0]} rows loaded")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=Path("data/generated"))
    load(parser.parse_args().dir)


if __name__ == "__main__":
    main()

