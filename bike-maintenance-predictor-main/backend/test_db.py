import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    print("? Connected OK to database:", os.getenv("DB_NAME"))
    conn.close()
except Exception as e:
    print("? Connection error:", repr(e))
