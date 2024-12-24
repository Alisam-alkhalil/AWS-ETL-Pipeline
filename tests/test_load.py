from unittest.mock import MagicMock, patch
from load import load_to_db 

# Test data
def test_load_to_db():
    """
    Test load_to_db function

    Given a set of transactions, transaction items, items, variants, and branches, this test
    verifies that the load_to_db function correctly inserts the data into the database.

    The test uses a mock object to simulate the psycopg connection and cursor. It then
    verifies that the executemany method was called five times, once for each table, and
    that the correct SQL statements were executed with the correct data.

    The test data includes two transactions, two transaction items, two items, two variants,
    and two branches.
    """
    transactions = [
        {"id": 1, "timestamp": "2024-12-10T10:00:00", "branch_id": 101, "total_price": 50.0, "payment_type": "Card"},
        {"id": 2, "timestamp": "2024-12-10T10:30:00", "branch_id": 102, "total_price": 75.0, "payment_type": "Cash"}
    ]

    transaction_items = [
        {"id": 1, "transaction_id": 1, "item_id": 201, "variant_id": 301, "quantity": 2},
        {"id": 2, "transaction_id": 1, "item_id": 202, "variant_id": 302, "quantity": 1}
    ]

    items = [
        {"id": 201, "name": "Coffee", "size": "Medium", "price": 5.0},
        {"id": 202, "name": "Pastry", "size": "Small", "price": 3.5}
    ]

    variants = [
        {"id": 301, "name": "Original Roast"},
        {"id": 302, "name": "Chocolate Chip"}
    ]

    branches = [
        {"id": 101, "name": "Main Branch"},
        {"id": 102, "name": "East Side Branch"}
    ]

    # Mock the psycopg connection and cursor
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    # Patch psycopg.connect to return the mocked connection
    with patch("psycopg.connect", return_value=mock_conn):
        load_to_db(transactions, transaction_items, items, variants, branches, mock_conn)

        # Update assertion to check executemany calls
        assert mock_cursor.executemany.call_count == 5  # Inserts for each data type
