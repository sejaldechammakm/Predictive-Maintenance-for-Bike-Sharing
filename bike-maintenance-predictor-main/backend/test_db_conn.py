# test_db_conn.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("Using DB_HOST:", os.getenv("DB_HOST"))
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("Postgres version:", cur.fetchone())
    cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY table_schema, table_name;")
    rows = cur.fetchall()
    print("User tables (schema.table):")
    for s, t in rows:
        print(f"  {s}.{t}")
    cur.close()
    conn.close()
    print("Connection test succeeded.")
except Exception as e:
    print("Connection test failed:", repr(e))
