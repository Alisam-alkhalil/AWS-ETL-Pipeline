# function to define processing data by removing sensitive data from the list of dictionaries generated in create_merged_csv
def depersonalise_data(data: list[dict], remove_headers: list[str] = None) -> list[dict]:
    """Removes specified columns (sensitive data) from the provided input data.
    Args:
        data (list[dict]): raw data as a list[dict].
        remove_headers (list[str], optional): the columns to remove from the data.
            If not specified, defaults to ['customer', 'card_number'].
    Returns:
        list[dict]: list of dictionaries with depersonalised data
    """
    depersonalised_data = []
    # remove_headers include the sensitive headers - customer and card_number columns that need to be removed
    if remove_headers is None:
        remove_headers = ['customer', 'card_number']

    for item in data:
        non_sensitive_data = {}
        for header, value in item.items():
            if header not in remove_headers:
                non_sensitive_data[header] = value
                # appends non-sensitive key:value pairs in rows to depersonalised_data list of dictionaries
        depersonalised_data.append(non_sensitive_data)

    return depersonalised_data