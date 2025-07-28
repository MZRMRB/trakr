import psycopg2
from psycopg2 import sql
import os
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# --- ✅ Utility Functions ---

def connect_to_db(dbname):
    return psycopg2.connect(
        dbname=dbname,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT
    )

def database_exists(conn, db_name):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        return cur.fetchone() is not None

def create_database(conn, db_name):
    # Set autocommit to True for database creation
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"✅ Database '{db_name}' created.")

# --- 📦 Create All Tables ---

def create_tables(conn):
    # Set autocommit to False for table creation
    conn.autocommit = False
    with conn.cursor() as cur:

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Route_List (
            sn SERIAL PRIMARY KEY,
            terminal_id TEXT,
            tracking_object TEXT,
            tracking_time TIMESTAMP,
            gps_x DOUBLE PRECISION,
            gps_y DOUBLE PRECISION
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Virtual_Fence (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            imei_or_object TEXT,
            fence_name TEXT,
            warn_type TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Alarms (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            imei TEXT,
            tracking_object TEXT,
            warn_type TEXT,
            time TIMESTAMP,
            check_the_time TIMESTAMP,
            check_time TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Tags (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            imei TEXT,
            signal INTEGER,
            power INTEGER,
            charge_status TEXT,
            tracking_update_time TIMESTAMP,
            data_update_time TIMESTAMP,
            bluetooth_mark TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Organizations (
            id SERIAL PRIMARY KEY,
            organization_name TEXT,
            title TEXT,
            product_type TEXT,
            create_time TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Accounts (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            account TEXT,
            permission TEXT,
            login_free_address TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Tracking_Objects (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            name TEXT,
            role TEXT,
            mac TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Roles (
            sn SERIAL PRIMARY KEY,
            organization TEXT,
            name TEXT,
            color TEXT
        )
        """)

        conn.commit()
        print("✅ All 8 tables created successfully (if not already present).")

# --- 🚀 Main Runner ---

def init_database():
    """Initialize the database and create tables if they don't exist."""
    try:
        print("🔍 Connecting to PostgreSQL...")
        conn = connect_to_db("postgres")  # Admin DB to check/create Trakr DB

        if not database_exists(conn, settings.DB_NAME):
            print(f"📂 Database '{settings.DB_NAME}' not found. Creating it...")
            create_database(conn, settings.DB_NAME)
        else:
            print(f"✅ Database '{settings.DB_NAME}' already exists.")

        conn.close()

        # Now connect to actual Trakr DB to create tables
        print(f"🔗 Connecting to '{settings.DB_NAME}' to create tables...")
        trakr_conn = connect_to_db(settings.DB_NAME)
        create_tables(trakr_conn)
        trakr_conn.close()

        print("🎉 Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"❌ Database initialization failed: {e}")
        # Don't raise the exception, just log it
        # This allows the app to start even if database is not available

if __name__ == "__main__":
    init_database() 