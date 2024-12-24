import pytest
from csv import DictWriter
from transform.unf_parsing import *

@pytest.fixture
def field_names() -> list[str]:
    """Pytest fixture for the field names of our data, without the test data
    included.

    Returns:
        list[str]: A list of the field names.
    """
    return [
        'timestamp',
        'branch',
        'customer_name',
        'transaction_items',
        'total_price',
        'payment_type',
        'card_number'
    ]

@pytest.fixture
def raw_data(field_names) -> tuple[list[str], list[dict]]:
    """Pytest fixture for the raw data.

    Returns:
        A tuple (headings, data) that contains the list[str] of headings and
        the list[dict] of raw data.
    """
    headings = field_names
    # pylint: disable=line-too-long
    data = [
        ['21/04/2024 09:00','Edinburgh','Jesse Franco','Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60','4.35','CASH',''],
        ['21/04/2024 09:01','Edinburgh','Rose Jackson','Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00','3.6','CARD','8032985528327355'],
        ['21/04/2024 09:03','Edinburgh','Albert Kenney','Large Flavoured iced latte - Hazelnut - 3.25','3.25','CARD','4067790083911858'],
        ['21/04/2024 09:05','Edinburgh','Carol Dickens','Regular Speciality Tea - Earl Grey - 1.30','1.3','CARD','3634783640542530'],
        ['21/04/2024 09:07','Edinburgh','Brenda Avila','Large Flavoured iced latte - Hazelnut - 3.25','3.25','CARD','4461004233326644'],
        ['21/04/2024 09:09','Edinburgh','Gladys Vandenbosch','Regular Americano - 1.95, Regular Speciality Tea - Green - 1.30, Regular Smoothies - Carrot Kick - 2.00, Regular Mocha - 2.30','7.55','CARD','5179414407798244'],
        ['21/04/2024 09:10','Edinburgh','Joyce Saadd','Large Speciality Tea - Fruit - 1.60, Large Smoothies - Glowing Greens - 2.50, Large Mocha - 2.70','6.8','CARD','3007856066766483']
    ]
    return headings, [dict(zip(headings, row)) for row in data]

@pytest.fixture
def tmp_data_path(tmp_path, raw_data):
    """Creates a temporary CSV file and returns the file path.

    Returns:
        str: the path to the temp CSV file.
    """
    new_path = tmp_path / 'tmp_data.csv'
    try:
        f = open(new_path, 'w', encoding='utf-8', newline='')
    except Exception as e:
        raise e
    # Only continuing if this was a success.
    with f:
        writer = DictWriter(f, fieldnames=raw_data[0])
        writer.writerows(raw_data[1])
    # Return out of context - we don't want to keep this open.
    return new_path
    # Normally would yield and clean up after but tmp_path will do that
    # for me.

def test_normalise_item_column(raw_data):
    """Tests that the UNF-1NF function correctly normalises the item list
    column.
    """
    example = raw_data[1][:1]
    # "Regular Flavoured iced latte - Hazelnut - 2.75, Large Speciality Tea - Green - 1.60"
    # "Large Speciality Tea - Green - 1.60, Regular Smoothies - Glowing Greens - 2.00"
    # TODO: Check this is correct (re: CSV values with ""s).
    #   Also, could always use more test data.
    expected_items = [
        {
            'item_size': 'Regular',
            'item_name': 'Flavoured iced latte',
            'item_variant': 'Hazelnut',
            'item_price': '2.75',
            'item_quantity': '1',
        },
        {
            'item_size': 'Large',
            'item_name': 'Speciality Tea',
            'item_variant': 'Green',
            'item_price': '1.60',
            'item_quantity': '1',
        },
    ]
    result = normalise_item_column(example)
    assert all(finalrow == finalrow | expected_items[i] for i, finalrow in enumerate(result))

def test_parse_str_to_list():
    """Tests that parse_str_to_list correctly splits and counts occurances of
    string components.
    """
    words = ['one', 'one', 'two', 'one', 'two', 'two', 'two', '3']
    test_data = ', '.join(words)
    assert parse_str_to_list(test_data) == [('two', 4), ('one', 3), ('3', 1)]

def test_split_item_string():
    """Tests the item string splitting method.
    """
    test_data = 'Regular Flavoured iced latte - Hazelnut - 2.75'
    assert split_item_string(test_data) == ('Regular',
                            'Flavoured iced latte', 'Hazelnut', '2.75')
