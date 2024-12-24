import csv
import time
from io import StringIO


def csv_to_dict(file: str | StringIO, headers: list[str] = ['timestamp', 'branch', 'customer', 'transaction_items', 'total_price', 'payment_type', 'card_number'] ):
    """
    Converts a CSV file to a list of dictionaries.

    Parameters:
        file (str): the path to the CSV file

    Returns:
        list[dict]: a list of dictionaries, where each dictionary represents a
            row in the CSV file
    """
    reader = csv.DictReader(file, fieldnames=headers)
    return list(reader)



def create_merged_csv(data: list[dict]):
    """
    Creates a new CSV file containing the merged data.

    Reads a list of dictionaries and writes them to a new CSV file, named
    "mergeddata_<current date>.csv".

    Parameters:
        data (list[dict]): a list of dictionaries, each representing a row in the
            merged CSV file

    Returns:
        None
    """
    with open(f'mergeddata_{time.strftime("%d-%m-%Y")}.csv', 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    
    

if __name__ == "__main__":
    create_merged_csv(csv_to_dict('edinburgh_21-04-2024_09-00-00.csv'))

    


