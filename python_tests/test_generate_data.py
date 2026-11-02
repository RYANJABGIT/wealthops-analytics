import csv
import hashlib
from datetime import date
from pathlib import Path

from scripts.generate_data import HEADERS, generate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_reproducible_csvs(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    counts1 = generate(a, profile="demo", seed=17, as_of=date(2026, 10, 30))
    counts2 = generate(b, profile="demo", seed=17, as_of=date(2026, 10, 30))
    assert counts1 == counts2
    assert all(digest(a / f"{table}.csv") == digest(b / f"{table}.csv") for table in HEADERS)


def test_relationships_and_valid_dates(tmp_path):
    generate(tmp_path, profile="demo")
    customers = {r["customer_id"] for r in records(tmp_path / "raw_customers.csv")}
    accounts = records(tmp_path / "raw_accounts.csv")
    account_ids = {r["account_id"] for r in accounts}
    opened = {r["account_id"]: r["opening_date"] for r in accounts}
    closed = {r["account_id"]: r["closing_date"] for r in accounts}
    assert all(r["customer_id"] in customers for r in accounts)
    for tx in records(tmp_path / "raw_transactions.csv"):
        assert tx["account_id"] in account_ids
        assert opened[tx["account_id"]] <= tx["transaction_date"]
        if closed[tx["account_id"]]:
            assert tx["transaction_date"] <= closed[tx["account_id"]]
    for val in records(tmp_path / "raw_valuations.csv"):
        assert val["account_id"] in account_ids
        assert opened[val["account_id"]] <= val["valuation_date"]
        if closed[val["account_id"]]:
            assert val["valuation_date"] <= closed[val["account_id"]]


def test_profile_sizes(tmp_path):
    result = generate(tmp_path, profile="demo")
    assert result["raw_customers"] == 60
    assert result["raw_accounts"] == 90
    assert result["raw_transactions"] == 400
    assert result["raw_valuations"] > 0

