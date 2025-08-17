from dotenv import load_dotenv
import os
from decimal import Decimal, InvalidOperation
import pandas as pd
import psycopg
import argparse

load_dotenv()  

def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def clean_amount(x):
    if pd.isna(x):
        return None
    s = str(x).strip().replace(",", "")
    for ch in ("£", "€", "$", "+"):
        s = s.replace(ch, "")
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Bad amount: {x!r}")

def clean_date(x):
    dt = pd.to_datetime(x, errors="coerce", dayfirst=False)
    if pd.isna(dt):
        raise ValueError(f"Bad date: {x!r}")
    return dt.date()

def get_or_create_account(conn, name, institution="YourBank", currency="GBP"):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT account_id FROM accounts WHERE name=%s AND institution=%s",
            (name, institution),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO accounts(name, institution, currency) VALUES (%s,%s,%s) RETURNING account_id",
            (name, institution, currency),
        )
        account_id = cur.fetchone()[0]
    conn.commit()
    return account_id

def import_csv(path, default_account="Main Current", default_institution="YourBank"):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")

    if "account" not in df.columns:
        df["account"] = default_account
    if "balance" not in df.columns:
        df["balance"] = None

    df["txn_date"] = df["date"].apply(clean_date)
    df["amount_clean"] = df["amount"].apply(clean_amount)
    df["description_clean"] = df["description"].astype(str).str.strip()
    df["account_clean"] = df["account"].astype(str).str.strip()
    df["balance_clean"] = df["balance"]

    inserted = 0
    skipped = 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            acct_cache = {}

            for row in df.itertuples(index=False):
                acct_name = getattr(row, "account_clean")
                if acct_name not in acct_cache:
                    acct_cache[acct_name] = get_or_create_account(
                        conn, acct_name, default_institution
                    )
                account_id = acct_cache[acct_name]

                cur.execute(
                    """
                    INSERT INTO transactions(account_id, txn_date, description, amount, balance, category_id, import_id)
                    VALUES (%s, %s, %s, %s, %s, NULL, NULL)
                    ON CONFLICT (account_id, txn_date, amount, description) DO NOTHING
                    """,
                    (
                        account_id,
                        getattr(row, "txn_date"),
                        getattr(row, "description_clean"),
                        getattr(row, "amount_clean"),
                        getattr(row, "balance_clean"),
                    ),
                )
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1

        conn.commit()

    print(f"Import complete: {inserted} inserted, {skipped} skipped (duplicates).")

def main():
    parser = argparse.ArgumentParser(description="Import transactions from a CSV file.")
    parser.add_argument("csv_path", help="Path to CSV (e.g., data/samples/sample_transactions.csv)")
    parser.add_argument("--account", default="Main Current")
    parser.add_argument("--institution", default="YourBank")
    args = parser.parse_args()
    import_csv(args.csv_path, default_account=args.account, default_institution=args.institution)

if __name__ == "__main__":
    main()
