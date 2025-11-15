"""
Database connection configuration for Smart Bottle ML Service
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
from typing import Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '211.192.7.222'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'smart_bottle'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
}

# Connection pool configuration
POOL_CONFIG = {
    'pool_name': 'smartbottle_ml_pool',
    'pool_size': 5,
    'pool_reset_session': True,
    'autocommit': True,
}

# Global connection pool
_connection_pool: Optional[pooling.MySQLConnectionPool] = None


def initialize_pool():
    """Initialize MySQL connection pool"""
    global _connection_pool

    if _connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return _connection_pool

    try:
        _connection_pool = pooling.MySQLConnectionPool(
            **POOL_CONFIG,
            **DB_CONFIG
        )
        logger.info(f"Connection pool initialized: {POOL_CONFIG['pool_name']}")
        return _connection_pool

    except mysql.connector.Error as err:
        logger.error(f"Failed to create connection pool: {err}")
        raise


def get_connection():
    """
    Get database connection from pool

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection

    Raises:
        Exception: If connection pool not initialized or connection fails
    """
    global _connection_pool

    if _connection_pool is None:
        logger.info("Connection pool not initialized, initializing now...")
        initialize_pool()

    try:
        connection = _connection_pool.get_connection()
        logger.debug("Database connection acquired from pool")
        return connection

    except mysql.connector.Error as err:
        logger.error(f"Failed to get connection: {err}")
        raise


def close_pool():
    """Close all connections in the pool"""
    global _connection_pool

    if _connection_pool is not None:
        try:
            # MySQL connection pool doesn't have explicit close method
            # Connections are automatically closed when object is destroyed
            _connection_pool = None
            logger.info("Connection pool closed")
        except Exception as err:
            logger.error(f"Error closing connection pool: {err}")


def test_connection() -> bool:
    """
    Test database connection

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result[0] == 1:
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed: unexpected result")
            return False

    except Exception as err:
        logger.error(f"Database connection test failed: {err}")
        return False


if __name__ == "__main__":
    # Test the connection
    logging.basicConfig(level=logging.INFO)

    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")

    close_pool()
