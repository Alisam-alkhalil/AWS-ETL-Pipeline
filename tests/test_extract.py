import csv
import sys
import pytest
from extract import csv_to_dict  

def test_csv_to_dict(tmp_path):
    """
    Tests the csv_to_dict function by verifying its ability to convert a CSV file
    into a list of dictionaries with specified headers.

    This test creates a temporary CSV file using sample data, calls the csv_to_dict
    function, and checks that the output matches the expected list of dictionaries.

    Parameters:
        tmp_path (pathlib.Path): A built-in pytest fixture that provides a temporary
        directory unique to the test invocation, used here to store the test CSV file.

    Asserts:
        The result from csv_to_dict matches the expected list of dictionaries.
    """
    # Define headers and sample data
    headers = ['timestamp', 'branch', 'customer', 'item', 'total_price', 'payment_type', 'card_number']
    data = [
        ['2023-12-03 12:00:00', 'London', 'Alice', 'Laptop', '1200.00', 'Credit', '1234-5678-9012-3456'],
        ['2023-12-03 13:00:00', 'Manchester', 'Bob', 'Phone', '800.00', 'Debit', '9876-5432-1098-7654']
    ]
    
    # Create a temporary CSV file
    csv_file = tmp_path / "test_data.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    # Call the function and check results
    result = csv_to_dict(str(csv_file), headers)
    
    # Expected output
    expected = [
        {
            'timestamp': '2023-12-03 12:00:00',
            'branch': 'London',
            'customer': 'Alice',
            'item': 'Laptop',
            'total_price': '1200.00',
            'payment_type': 'Credit',
            'card_number': '1234-5678-9012-3456'
        },
        {
            'timestamp': '2023-12-03 13:00:00',
            'branch': 'Manchester',
            'customer': 'Bob',
            'item': 'Phone',
            'total_price': '800.00',
            'payment_type': 'Debit',
            'card_number': '9876-5432-1098-7654'
        }
    ]
    
    assert result == expected