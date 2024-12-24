"""Module containing a function that parses a table (list of dictionaries)
into a version that satisfies 1NF for use in a postgres table, as well as
some utility methods to aid in doing so.
"""

from uuid import uuid4
from collections import Counter


def normalise_item_column(
        data: list[dict[str, str]],
        target_column: str = "transaction_items",
        **item_details: dict[str, str]
    ) -> list[dict[str, str]]:
    """Modifies a table containing an unnormalised transaction_items column,
    replacing that column with a set of columns satisfying 1NF and adding an
    id column.

    By default, this function will break the transaction_items column into
    item_size, item_name, item_variant, item_price, and item_quantity columns,
    where item_variant may be None.

    This function also assumes the incoming data is uniform, i.e. that every
    dictionary in the list has the same set of keys, (which should not already
    include an id column - this will replace any existing column of that name.)
    
    Args:
        data (list[dict[str, str]]): The unnormalised data.
        target_column (str): The name of the column (dictionary key) to break
            into multiple item columns.
        **item_details: Optional replacements for the output columns, e.g.
            `item_variant='item_flavour'` will rename the item variant column
            in the returned data.

    Returns:
        list[dict[str, str]]: The resulting normalised data. The intended PK
            of this output is a composite of (id, item_name).
    """
    default_details = ('item_size', 'item_name', 'item_variant', 'item_price',
            'item_quantity')
    # order matters here, so we use a tuple (even though it should be fine
    # to use whatever in >=3.9)
    item_columns = tuple(item_details.get(x, x) for x in default_details)
    # Exclude the target column.
    keys = tuple(x for x in data[0].keys() if x != target_column)
    new_data = []
    for transaction in data:
        # Copy other keys immediately
        new_item = {k: transaction[k] for k in keys}
        # We need to add a new column for each distinct item in the
        # transaction, and an id to associate them all.
        new_item['id'] = str(uuid4())
        for item, qty in parse_str_to_list(transaction['transaction_items']):
            # Tuple of the data in order.
            item_data = split_item_string(item) + (str(qty),)
            # Build mapping of columns to data, merge into row and add.
            item_dict = dict(zip(item_columns, item_data))
            row = new_item | item_dict
            new_data.append(row)
    return new_data

def parse_str_to_list(string: str) -> list[tuple[str, int]]:
    """Converts a comma-separated list of strings into a python list of
    tuples.

    This method also strips any extra whitespace from the name.
    Each tuple is of the form (name, amount), where amount is the number
        of times that item appears in the list.

    Args:
        string (str): The comma-separated list as a string.

    Returns:
        list[tuple[str, int]]: A python list of tuples, which denote the unique
            items and how many times that item occured in the order.
    """
    counted = Counter([s.strip() for s in string.split(',')])
    return counted.most_common()

def split_item_string(string: str) -> tuple[str, str, str, str]:
    """Splits a string representing an item's details into a tuple of the form
    (size, name, variant, price).

    This function expects a string of the form:
        SIZE ITEM[ - VARIANT] - PRICE
    
    All types in the return are strings, to ensure that no floating point
    imprecision impacts the pricing data.

    Args:
        string (str): The string describing the item.

    Returns:
        tuple[str, str, str, str]: A tuple containing the size, name, variant,
        and price of the item, all as strings. variant may be None.
    """
    # The size is always the first word, and always 1 word.
    size, rest = string.split(maxsplit=1)
    match rest.split(' - '):
        case [name, variant, price]:
            return size, name, variant, price
        case [name, price]:
            return size, name, None, price
        case _:
            raise ValueError("Unexpected item detail syntax.")
