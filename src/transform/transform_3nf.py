from uuid import uuid4  # For generating GUIDs

def normalise_branches(data: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Normalise branches into a separate table with unique GUIDs.

    This function returns a modified transaction table (which contains a
    branch_id column), and a branch table (which links those branch_ids with
    specific cafe branches in our data.) In doing so, this function removes
    the (implied) transitive dependency in order to satisfy 3NF.

    Args:
        data (list[dict]): Input (2NF) data containing transaction and branch details.

    Returns:
        A tuple (branches, transactions), where branches is a list of
            dictionaries representing rows of the branch table, and
            transactions is a list of dictionaries representing rows of the
            transaction table.
    """
    branches = []  # List of dictionaries to hold unique branches
    transactions = []  # List to hold updated transaction data
    branch_ids = {}  # Quick lookup map for branch GUIDs

    for row in data:  # TODO: 'branch' col name could also be passed in as an argument.
        branch = row["branch"]  # Extract the branch name from the row
        if branch not in branch_ids:
            # Generate a unique ID for the branch
            branch_id = str(uuid4())
            branch_ids[branch] = branch_id
            # Add the branch to the branches table
            branches.append({"id": branch_id, "name": branch})

        # Copy old data, replace branch key with new branch_id.
        new_transaction = row.copy()
        del new_transaction['branch']
        new_transaction['branch_id'] = branch_ids[branch]

        transactions.append(new_transaction)

    # Return the branches and updated transactions
    return branches, transactions

def normalise_items_and_transactions(
    transactions: list[dict]
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """
    Normalise items and link them via transaction items and variants tables.

    This function aims to remove the partial dependencies between the item
    detail columns and the composite key of (transaction_id, item_name,
    item_size), in order to satisfy 2NF.

    Args:
        transactions (list[dict]): A list of dictionaries containing
            transaction data (in 1NF).

    Returns:
        A tuple (transactions, items, variants, transaction_items) of
            list[dict]s that represent rows of the transaction, item, variant,
            and transaction_item tables of our database schema.
    """
    items = []  # Dictionary to hold unique items
    variants = []  # to store unique variants
    transaction_items = []  # to store transaction-item-variant mapping
    new_transactions = []
    item_ids = {}  # To keep track of items already added
    variant_ids = {}  # to track added variants

    for row in transactions:
        # Copy everything except the item details
        modified_row = {k: row[k] for k in row if k not in [
            'item_name', 'item_size', 'item_variant',
            'item_quantity', 'item_price'
        ]}  # TODO: This could be passed in as an argument.
        item_name = row["item_name"]  # Extract item name
        size = row["item_size"]
        variant_name = row["item_variant"]
        quantity = row["item_quantity"]

        # We have 1 id per name + size combo in the schema
        if (item_name, size) not in item_ids:
            item_id = str(uuid4())
            item_ids[(item_name, size)] = item_id
            items.append({
                "id": item_id,
                "name": item_name,
                "size": size,
                "price": row["item_price"]
            })

        # Add variant if not already in the variants table
        if variant_name not in variant_ids:
            variant_id = str(uuid4())
            variant_ids[variant_name] = variant_id
            variants.append({
                "id": variant_id,
                "name": variant_name
            })

        # Add transaction item
        transaction_items.append({
            "id": str(uuid4()),
            "transaction_id": row["id"],
            "item_id": item_ids[(item_name, size)],
            "variant_id": variant_ids[variant_name],
            "quantity": quantity
        })

        # Add modified row to the new table
        new_transactions.append(modified_row)

    return new_transactions, items, variants, transaction_items
