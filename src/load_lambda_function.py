from io import StringIO
import os
import time
import boto3
import psycopg
import json
import csv
import uuid
from dotenv import load_dotenv
from load import load_to_db
from load import create_merged_csv
from load_schema import create_tables
from urllib.parse import unquote_plus
import logging

TABLES = ('transaction', 'transaction_item', 'item', 'variant', 'branch')

logger = logging.getLogger(__name__)

s3_client = boto3.client("s3")
ssm_client = boto3.client('ssm')

creds_param = ssm_client.get_parameter(Name=os.environ['SSM_PARAMETER_NAME'])

if creds_param.get('ResponseMetadata').get('HTTPStatusCode') == 200:
    val = creds_param['Parameter']['Value']
    creds = json.loads(val)

    host = creds['host']
    dbname = creds['database-name']
    port = creds['port']
    user = creds['user']
    password = creds['password']

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
    logger.setLevel("DEBUG")
    logger.debug("Getting aws_account")
    my_arn = context.invoked_function_arn
    aws_account = my_arn.split(":")[4]

    logger.info("Set up logger for load step.")
    error_flag = False
    for record in event.get("Records", []):
        logger.info("Handling new record: %s", record)
        match record.get("eventSource"):
            case 'aws:sqs':
                branch_name = record['body']
                logger.info("Loading tables for %s branch", branch_name)
                # Do 5 DB loads here.

                logger.info("Connecting to redshift...")
                with psycopg.connect(port=port, user=user, password=password, dbname=dbname, host=host, options='-c client_encoding=UTF8') as conn:
                    # TODO: consider not doing this?
                    logger.info("Connected to redshift, creating tables...")
                    create_tables(conn)

                    for table in TABLES:
                        file = f"{table}-{branch_name}.csv"
                        load_to_db(file, table, conn, aws_account, bucket_name='coffeetl-project-transformed-data')
                    logger.info("Load done!")
            case 'aws:s3': # Basically depricated.
                bucket_name = record["s3"]["bucket"]["name"]
                object_key = unquote_plus(record['s3']['object']['key'])
                filename = os.path.basename(object_key)
                logger.debug("Object key: %s\nFilename: %s",
                    object_key, filename)
                if not object_key.endswith(".csv"):
                    return {
                        'statusCode': 300,
                        'body': 'Unsupported file'
                    }
                # This should work, as long as no table contains a - in
                # its name.
                # We use _s to separate words in table names.
                # Notably, branch names with -s are handled correctly due
                # to maxsplit=1.
                target_table, _ = object_key.split('-', maxsplit=1)
                if target_table not in TABLES:
                    error_flag = True
                    logger.critical("Incoming table (%s) not recognised.", target_table)
                    continue

                logger.info("Connecting to redshift...")
                with psycopg.connect(port=port, user=user, password=password, dbname=dbname, host=host, options='-c client_encoding=UTF8') as conn:
                    logger.info("Connected to redshift, creating tables...")
                    create_tables(conn)
                    logger.info("Tables created, loading data...")
                    load_to_db(filename, target_table, conn, aws_account, bucket_name=bucket_name)
                    logger.info("ETL Done!")
            case _:
                error_flag = True
                logger.warning("Unsupported event record: %s", record)
                continue
    if error_flag:
        return {
            'statusCode': 300,
            'body': 'Lambda finished without processing all data.'
        }
    return {
        'statusCode': 200,
        'body': 'Lambda finished without errors.'
    }
