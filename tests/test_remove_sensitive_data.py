import pytest
from remove_sensitive_data import depersonalise_data

def test_depersonalise_data():
    """Tests that depersonalise_data correctly removes sensitive data.
    """
    # Using dummy data as the input list of dictionaries
    test_exported_data = [
        {
            'timestamp': '21/04/2024 09:00',
            'branch': 'Edinburgh',
            'customer': 'Jesse Franco',
            'item': 'Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60',
            'total_price': '4.35',
            'payment_type': 'CASH',
            'card_number': ''
        },
        {
            'timestamp': '21/04/2024 09:01',
            'branch': 'Edinburgh',
            'customer': 'Rose Jackson',
            'item': 'Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00',
            'total_price': '3.6',
            'payment_type': 'CARD',
            'card_number': '8032985528327355'
        }
    ]

    # The expected output after removing sensitive data ('customer' and 'card_number')
    expected_depersonalised_data = [
        {
            'timestamp': '21/04/2024 09:00',
            'branch': 'Edinburgh',
            'item': 'Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60',
            'total_price': '4.35',
            'payment_type': 'CASH'
        },
        {
            'timestamp': '21/04/2024 09:01',
            'branch': 'Edinburgh',
            'item': 'Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00',
            'total_price': '3.6',
            'payment_type': 'CARD'
        }
    ]

    result = depersonalise_data(test_exported_data)

    assert result == expected_depersonalised_data, \
    "The depersonalised data does not match the expected result."

def test_depersonalise_data_empty():
    """Tests that depersonalise_data correctly returns an empty list when passed an empty list.
    """
    test_exported_data = []
    expected_depersonalised_data = []

    result = depersonalise_data(test_exported_data)

    assert result == expected_depersonalised_data, \
    f"The depersonalised data does not match the expected result."

def test_depersonalise_data_depersonalised():
    """Tests that depersonalise_data correctly returns a list of dictionaries when passed a list of already depersonalised dictionaries.
    """
    test_exported_data = [ {
            'timestamp': '21/04/2024 09:00',
            'branch': 'Edinburgh',
            'item': 'Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60',
            'total_price': '4.35',
            'payment_type': 'CASH'
        },
        {
            'timestamp': '21/04/2024 09:01',
            'branch': 'Edinburgh',
            'item': 'Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00',
            'total_price': '3.6',
            'payment_type': 'CARD'
        }
    ]
    
    expected_depersonalised_data = [ {
            'timestamp': '21/04/2024 09:00',
            'branch': 'Edinburgh',
            'item': 'Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60',
            'total_price': '4.35',
            'payment_type': 'CASH'
        },
        {
            'timestamp': '21/04/2024 09:01',
            'branch': 'Edinburgh',
            'item': 'Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00',
            'total_price': '3.6',
            'payment_type': 'CARD'
        }
    ]

    result = depersonalise_data(test_exported_data)

    assert result == expected_depersonalised_data, \
    f"The depersonalised data does not match the expected result."

    