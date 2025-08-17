from dotenv import load_dotenv
import os
import psycopg

load_dotenv()

def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def apply_rules():
    sql = """
    UPDATE transactions t
    SET category_id = r.category_id
    FROM rules r
    WHERE t.category_id IS NULL
      AND t.description ILIKE '%' || r.pattern || '%';
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            updated = cur.rowcount
        conn.commit()
    print(f"Applied rules. Categorised {updated} transactions.")

if __name__ == "__main__":
    apply_rules()
