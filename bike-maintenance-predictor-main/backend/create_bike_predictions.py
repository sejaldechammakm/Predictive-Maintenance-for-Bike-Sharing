# create_bike_predictions.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Connecting to:", DB_HOST, DB_PORT, DB_NAME, DB_USER)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS public.bike_predictions (
        bike_id TEXT PRIMARY KEY,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        failure_probability DOUBLE PRECISION
    );
    """)

    rows = [
        ("B001", 12.9716, 77.5946, 0.85),
        ("B002", 28.7041, 77.1025, 0.12),
        ("B003", 19.0760, 72.8777, 0.46),
        ("B004", 13.0827, 80.2707, 0.02),
        ("B005", 22.5726, 88.3639, 0.66)
    ]

    cur.executemany(
        "INSERT INTO public.bike_predictions (bike_id, latitude, longitude, failure_probability) VALUES (%s, %s, %s, %s) ON CONFLICT (bike_id) DO UPDATE SET latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude, failure_probability=EXCLUDED.failure_probability;",
        rows
    )

    conn.commit()
    print("✅ Table created and sample data inserted.")
    cur.execute("SELECT * FROM public.bike_predictions;")
    print("Sample rows:")
    for r in cur.fetchall():
        print(r)

    cur.close()
    conn.close()
    print("All done.")
except Exception as e:
    print("❌ ERROR:", e)
