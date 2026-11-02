"""Deterministic synthetic wealth-management data. No real client information."""
from __future__ import annotations

import argparse
import csv
import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HEADERS = {
    "raw_customers": ["customer_id", "registration_date", "country", "customer_segment",
                      "customer_status", "updated_at", "loaded_at"],
    "raw_accounts": ["account_id", "customer_id", "product_type", "opening_date",
                     "closing_date", "account_status", "partner_id", "updated_at", "loaded_at"],
    "raw_transactions": ["transaction_id", "account_id", "transaction_type",
                         "transaction_amount", "currency", "transaction_date",
                         "transaction_status", "updated_at", "loaded_at"],
    "raw_valuations": ["account_id", "valuation_date", "total_value", "cash_value",
                       "currency", "updated_at", "loaded_at"],
    "raw_fee_events": ["fee_id", "account_id", "fee_date", "fee_type", "fee_amount",
                       "fee_status", "updated_at", "loaded_at"],
    "raw_partner_valuations": ["partner_id", "account_id", "valuation_date",
                               "partner_value", "currency", "updated_at", "loaded_at"],
}
SIZES = {
    "demo": {"customers": 60, "accounts": 90, "transactions": 400, "days": 30},
    "full": {"customers": 2000, "accounts": 3000, "transactions": 60000, "days": 365},
}
PRODUCTS = ("ASSURANCE_VIE", "PEA", "PER")
PARTNERS = ("P-01", "P-02", "P-03", "P-04")


def money(value: Decimal | float | int) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def generate(output_dir: Path, profile: str = "demo", seed: int = 42,
             as_of: date = date(2026, 10, 30)) -> dict[str, int]:
    """Generate CSV files. Fixed seed and as_of produce byte-identical outputs."""
    if profile not in SIZES:
        raise ValueError(f"Unknown profile: {profile}")
    cfg = SIZES[profile]
    rng = random.Random(seed)
    start = as_of - timedelta(days=cfg["days"] - 1)
    loaded_at = datetime.combine(as_of + timedelta(days=1), datetime.min.time(),
                                 tzinfo=timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    handles = {}
    writers = {}
    try:
        for name, header in HEADERS.items():
            handle = (output_dir / f"{name}.csv").open("w", newline="", encoding="utf-8")
            handles[name] = handle
            writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
            writer.writeheader()
            writers[name] = writer
            counts[name] = 0

        def emit(table: str, row: dict) -> None:
            writers[table].writerow(row)
            counts[table] += 1

        customers = []
        for i in range(cfg["customers"]):
            customer_id = f"C{i + 1:06d}"
            registered = start - timedelta(days=rng.randint(1, 800))
            customers.append(customer_id)
            emit("raw_customers", {
                "customer_id": customer_id, "registration_date": registered.isoformat(),
                "country": rng.choice(["FR", "FR", "FR", "BE", "DE"]),
                "customer_segment": rng.choice(["MASS", "AFFLUENT", "PRIVATE"]),
                "customer_status": "ACTIVE",
                "updated_at": loaded_at, "loaded_at": loaded_at,
            })

        accounts = []
        for i in range(cfg["accounts"]):
            account_id = f"A{i + 1:07d}"
            opened = start - timedelta(days=rng.randint(0, 365))
            partner_id = rng.choice(PARTNERS)
            closed = as_of - timedelta(days=rng.randint(1, max(1, cfg["days"] // 3))) if rng.random() < 0.03 else None
            accounts.append((account_id, opened, closed, partner_id))
            emit("raw_accounts", {
                "account_id": account_id, "customer_id": rng.choice(customers),
                "product_type": rng.choice(PRODUCTS), "opening_date": opened.isoformat(),
                "closing_date": closed.isoformat() if closed else "",
                "account_status": "CLOSED" if closed else "OPEN",
                "partner_id": partner_id, "updated_at": loaded_at, "loaded_at": loaded_at,
            })

        for i in range(cfg["transactions"]):
            account_id, opened, closed, _ = rng.choice(accounts)
            last = closed or as_of
            first = max(start, opened)
            when = first + timedelta(days=rng.randint(0, (last - first).days))
            txn_type = rng.choices(
                ["deposit", "withdrawal", "internal_transfer_in", "internal_transfer_out"],
                [50, 30, 10, 10],
            )[0]
            emit("raw_transactions", {
                "transaction_id": f"T{i + 1:09d}", "account_id": account_id,
                "transaction_type": txn_type, "transaction_amount": money(rng.randint(20, 9000)),
                "currency": "EUR", "transaction_date": when.isoformat(),
                "transaction_status": rng.choices(
                    ["completed", "pending", "rejected", "cancelled"], [85, 7, 4, 4]
                )[0], "updated_at": loaded_at, "loaded_at": loaded_at,
            })

        fee_index = 0
        for account_id, opened, closed, partner_id in accounts:
            balance = Decimal(rng.randint(5000, 95000))
            cash = balance * Decimal("0.08")
            for day_offset in range(cfg["days"]):
                d = start + timedelta(days=day_offset)
                if d < opened or (closed and d > closed):
                    continue
                balance = max(Decimal("0.00"), balance + Decimal(rng.randint(-140, 165)))
                cash = max(Decimal("0.00"), min(balance, cash + Decimal(rng.randint(-15, 20))))
                emit("raw_valuations", {
                    "account_id": account_id, "valuation_date": d.isoformat(),
                    "total_value": money(balance), "cash_value": money(cash),
                    "currency": "EUR", "updated_at": loaded_at, "loaded_at": loaded_at,
                })
                if day_offset % 7 == 0 and rng.random() < 0.45:
                    emit("raw_partner_valuations", {
                        "partner_id": partner_id, "account_id": account_id,
                        "valuation_date": d.isoformat(),
                        "partner_value": money(balance + Decimal(rng.choice([0, 0, 0, 2, -2, 50]))),
                        "currency": "EUR", "updated_at": loaded_at, "loaded_at": loaded_at,
                    })
                if day_offset > 0 and day_offset % 30 == 0:
                    fee_index += 1
                    emit("raw_fee_events", {
                        "fee_id": f"F{fee_index:09d}", "account_id": account_id,
                        "fee_date": d.isoformat(), "fee_type": "management",
                        "fee_amount": money(balance * Decimal("0.00015")),
                        "fee_status": "posted", "updated_at": loaded_at, "loaded_at": loaded_at,
                    })
    finally:
        for handle in handles.values():
            handle.close()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(SIZES), default="demo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date(2026, 10, 30))
    parser.add_argument("--out", type=Path, default=Path("data/generated"))
    args = parser.parse_args()
    counts = generate(args.out, args.profile, args.seed, args.as_of)
    for table, count in counts.items():
        print(f"{table}: {count:,} rows")


if __name__ == "__main__":
    main()

