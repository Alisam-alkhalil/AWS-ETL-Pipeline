from io import StringIO
import os
import time
import boto3
import psycopg
import csv
import uuid
from dotenv import load_dotenv
from extract import csv_to_dict, create_merged_csv
from remove_sensitive_data import depersonalise_data
from transform.unf_parsing import normalise_item_column
from transform.transform_3nf import normalise_items_and_transactions, normalise_branches
from transform.deduplicate import deduplicate
from load import create_merged_csv
from load_schema import create_tables
from urllib.parse import unquote_plus, quote_plus
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.setLevel("DEBUG")


s3_client = boto3.client("s3")
sqs = boto3.client("sqs")


def lambda_handler(event, context):
    """
    AWS Lambda function to process CSV files from S3 events.

    This function is triggered by S3 events and processes CSV files by 
    extracting the records, depersonalizing sensitive information, and 
    printing the processed data. It expects the event to contain S3 
    bucket and object information.

    Args:
        event (dict): The event data containing S3 bucket and object 
                      details.
        context (object): The context in which the function is called, 
                          providing runtime information.

    Returns:
        dict: A response with a status code and a message indicating 
              the processing result.
    """
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel("DEBUG")
    logger.info("Set up logger.")
    for record in event["Records"]:
        # Log new record
        logger.info("Handling new record: %s", record)
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = unquote_plus(record["s3"]["object"]["key"])
        logger.debug("Object key: %s", object_key)

        if object_key.endswith(".csv"):
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            logger.info("Getting CSV data")
            csv_content = response["Body"].read().decode("utf-8")
            logger.debug("CSV content: %s", csv_content)
        else:
            return {
                'statusCode': 300,
                'body': 'Unsupported file'
            }

        # We use StringIO to convert the CSV content into a file-like object
        # that we can then pass to csv_to_dict
        logger.info("Starting extract...")
        data = csv_to_dict(StringIO(csv_content))

        logger.info("Converting data to list[dict]...")
        impersonal_data = depersonalise_data(data, ['customer', 'card_number'])

        logger.info("Processing data...")
        logger.debug(impersonal_data)
        second_normalised_form = normalise_item_column(impersonal_data)

        third_normalised_branches = normalise_branches(second_normalised_form)

        third_normalised_transactions = normalise_items_and_transactions(third_normalised_branches[1])

        transactions = deduplicate(third_normalised_transactions[0])
        items = deduplicate(third_normalised_transactions[1])
        variants = deduplicate(third_normalised_transactions[2])
        transaction_items = deduplicate(third_normalised_transactions[3])
        branches = deduplicate(third_normalised_branches[0])

        logger.info("Transformations done, uploading transformed csv's...")

        branch_name = branches[0]["name"]
        
        filename = {
            "transaction": f"transaction-{branch_name}.csv",
            "item": f"item-{branch_name}.csv",
            "variant": f"variant-{branch_name}.csv",
            "transaction_item": f"transaction_item-{branch_name}.csv",
            "branch": f"branch-{branch_name}.csv"
        }

        create_merged_csv(transactions, bucket_name="coffeetl-project-transformed-data", filename = filename["transaction"])
        create_merged_csv(items, bucket_name="coffeetl-project-transformed-data", filename = filename["item"])
        create_merged_csv(variants, bucket_name="coffeetl-project-transformed-data", filename = filename["variant"])
        create_merged_csv(transaction_items, bucket_name="coffeetl-project-transformed-data", filename = filename["transaction_item"])
        create_merged_csv(branches, bucket_name="coffeetl-project-transformed-data", filename = filename["branch"])

        logger.info("CSVs uploaded, sending SQS message...")
        
        branch_enc = quote_plus(branch_name)
        queue_url = sqs.get_queue_url(QueueName='coffeetl-load-queue.fifo').get('QueueUrl')
        if not queue_url:
            logger.error("Could not get the URL of queue %s.",
                        'coffeetl-load-queue.fifo')
            return {
                'statusCode': 300,
                'body': 'Data extracted and transformed successfully, but '
                'failed to notify the queue.'
            }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=branch_name,
            MessageGroupId=branch_enc
        )

    return {
        'statusCode': 200,
        'body': 'File processed successfully!'
    }