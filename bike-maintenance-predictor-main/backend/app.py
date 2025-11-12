# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import pool

# Load .env (ensure .env is at project root)
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bike-api")

# Env vars (fallbacks)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_MINCONN = int(os.getenv("DB_MINCONN", 1))
DB_MAXCONN = int(os.getenv("DB_MAXCONN", 5))

app = FastAPI(title="Bike Management API")

# CORS: allow localhost dev origins commonly used in Windows dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.21.85.28:3000"  # Your Windows local IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_pool: pool.SimpleConnectionPool | None = None

@app.on_event("startup")
def startup():
    global db_pool
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        logger.warning("One or more DB environment variables are missing. Check .env file.")
    try:
        db_port_int = int(DB_PORT)
    except Exception:
        db_port_int = 5432
        logger.warning("Invalid DB_PORT; falling back to 5432")

    try:
        logger.info("Initializing DB connection pool...")
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=DB_MINCONN,
            maxconn=DB_MAXCONN,
            host=DB_HOST,
            port=db_port_int,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        logger.info("DB pool initialized.")
    except Exception as e:
        logger.exception("Failed to initialize DB pool: %s", e)
        db_pool = None

@app.on_event("shutdown")
def shutdown():
    global db_pool
    if db_pool:
        try:
            db_pool.closeall()
            logger.info("Closed DB connection pool.")
        except Exception:
            logger.exception("Error closing DB pool.")

@app.get("/")
def read_root():
    return {"message": "Welcome to Bike Management API"}

@app.get("/predictions")
def get_predictions(limit: int = 500):
    """
    Returns bike predictions ordered by failure_probability desc.
    Query param: limit (default 500)
    """
    global db_pool
    if db_pool is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    conn = None
    try:
        conn = db_pool.getconn()
        sql = """
            SELECT bike_id, latitude, longitude, failure_probability
            FROM bike_predictions
            ORDER BY failure_probability DESC
            LIMIT %s
        """
        # pandas will use the psycopg2 connection
        df = pd.read_sql(sql, conn, params=(limit,))
        # sanitize numerics
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

        # ensure types
        if 'failure_probability' in df.columns:
            df['failure_probability'] = df['failure_probability'].astype(float)
        if 'latitude' in df.columns:
            df['latitude'] = df['latitude'].astype(float)
        if 'longitude' in df.columns:
            df['longitude'] = df['longitude'].astype(float)

        records = df.to_dict(orient="records")
        return JSONResponse(content=records)
    except Exception as e:
        logger.exception("Error fetching predictions: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch predictions")
    finally:
        if conn and db_pool:
            try:
                db_pool.putconn(conn)
            except Exception:
                logger.exception("Failed to return connection to pool")
