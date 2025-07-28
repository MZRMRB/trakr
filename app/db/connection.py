import psycopg2
from psycopg2 import pool
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Global pool variable
_pool = None

def get_pool():
    """Get or create the connection pool"""
    global _pool
    if _pool is None:
        try:
            _pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
        except psycopg2.OperationalError as e:
            logger.warning(f"Database connection failed: {e}")
            # Return None if database doesn't exist yet
            return None
    return _pool

def get_conn():
    """Get a connection from the pool"""
    pool_instance = get_pool()
    if pool_instance is None:
        # If pool creation failed, try direct connection
        try:
            conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            yield conn
            conn.close()
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            raise
    else:
        conn = pool_instance.getconn()
        try:
            yield conn
        finally:
            pool_instance.putconn(conn) 