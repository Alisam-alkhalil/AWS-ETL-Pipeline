import os
import psycopg
import logging

logger = logging.getLogger(__name__)

def create_tables(conn: psycopg.connection):

    """
    Creates necessary tables in the database for the application.

    This function establishes the following tables if they do not already exist:
    - 'transaction': Stores transaction details with fields such as 
      transaction_id, timestamp, branch_id, total_price, and payment_type.
    - 'branch': Stores branch information with fields such as 
      branch_id and branch.
    - 'item': Stores item information with fields such as 
      item_id, item, and item_price.
    - 'transaction_item': Stores information about items in a transaction with fields 
      such as transaction_id, item_id, and quantity.
    - 'variant': Stores variant information with fields such as
      variant_id and variant_name.

    Parameters:
        conn (psycopg.connection): A connection object to the PostgreSQL database.

    Returns:
        None
    """
    logger.setLevel("DEBUG")
    logger.debug("Making cursor...")
    with conn.cursor() as cursor:
            logger.debug("Creating tables...")
            # Create the 'transaction' table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction (
                id VARCHAR(36),            
                timestamp TIMESTAMP,
                branch_id VARCHAR(36),
                total_price DECIMAL(10, 2),
                payment_type VARCHAR(255)
            );
            """)

            # Create the 'branch' table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS branch (
                id VARCHAR(36),
                name VARCHAR(255)
            );
            """)

            # Create the 'item' table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS item (
                id VARCHAR(36),
                name VARCHAR(255),
                size VARCHAR(255),
                price DECIMAL(10, 2)
            );
            """)

            # Create the 'transaction_item' table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_item (
                id VARCHAR(36),
                transaction_id VARCHAR(36),
                item_id VARCHAR(36),
                variant_id VARCHAR(36),
                quantity int
            );
            """)  

            # Create the 'variant' table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS variant (
                id VARCHAR(36),
                name VARCHAR(255)
            );
            """)
            logger.debug("Committing changes...")
            conn.commit()
            logger.debug("Done creating tables!")

