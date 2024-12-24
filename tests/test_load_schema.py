from unittest.mock import MagicMock, patch
from load_schema import create_tables

# Test data
def test_load_to_db():
    
    # Mock the psycopg connection and cursor
    """
    Tests the create_tables function by verifying that it executes the correct
    number of SQL statements to create tables in the database.

    This test uses mocking to simulate the psycopg connection and cursor, and
    patches the psycopg.connect function to return the mocked connection. 
    The test then calls create_tables with the mocked connection and asserts
    that the execute method on the cursor is called exactly five times, 
    corresponding to the creation of five tables.

    Asserts:
        The execute method on the mock cursor is called five times.
    """
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    # Patch psycopg.connect to return the mocked connection
    with patch("psycopg.connect", return_value=mock_conn):
        create_tables(mock_conn)

        # Update assertion to check execute calls
        assert mock_cursor.execute.call_count == 5 

        