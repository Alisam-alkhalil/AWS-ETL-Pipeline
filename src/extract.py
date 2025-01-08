import csv
import time
import boto3
from io import StringIO

s3 = boto3.client('s3')

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



def create_merged_csv(data: list[dict], bucket_name: str, filename: str):
    
    """
    Creates a new CSV file containing the merged data.

    Reads a list of dictionaries and writes them to a new CSV file, named
    filename, and uploads it to the bucket named bucket_name.

    Parameters:
        data (list[dict]): a list of dictionaries, each representing a row in the
            merged CSV file
        bucket_name (str): the name of the S3 bucket to which the merged CSV
            file should be uploaded
        filename (str): the name of the merged CSV file

    Returns:
        None
    """

    with open(f"/tmp/{filename}", 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writerows(data)

    s3.upload_file(f"/tmp/{filename}", bucket_name, filename)

    

    


