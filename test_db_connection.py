from dotenv import load_dotenv
import os
import psycopg

load_dotenv() 
conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
with conn.cursor() as cur:
    cur.execute("SELECT current_database(), current_user, version();")
    db, usr, ver = cur.fetchone()
    print("Connected to:", db, "as", usr)
    print(ver.splitlines()[0])
conn.close()
