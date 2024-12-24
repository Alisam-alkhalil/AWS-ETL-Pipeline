import os
import psycopg
import logging
import csv
import boto3
import json

logger = logging.getLogger(__name__)

s3_client = boto3.client("s3")


def create_merged_csv(data: list[dict], bucket_name: str, filename):

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

    s3_client.upload_file(f"/tmp/{filename}", bucket_name, filename)


def load_to_db(
        filename: str,
        target_table: str, 
        conn: psycopg.Connection,
        aws_account: str,
        bucket_name: str) -> None:
   
    """
    Copies the contents of a CSV file from S3 to a PostgreSQL table.

    Parameters:
        filename (str): the name of the CSV file to be copied
        target_table (str): the name of the PostgreSQL table to which the
            file should be copied
        conn (psycopg.Connection): an open connection to the PostgreSQL
            database
        bucket_name (str): the name of the S3 bucket in which the CSV file
            is stored

    Returns:
        None
    """

    logger.debug("Making cursor...")

    with conn.cursor() as cur:


        logger.debug(f"Inserting transactions into {target_table} table...")
        if target_table == "transaction":
            cur.execute(f"""
                COPY transaction (timestamp, total_price, payment_type, id, branch_id)
                FROM 's3://{bucket_name}/{filename}'
                IAM_ROLE 'arn:aws:iam::{aws_account}:role/RedshiftS3Role'
                CSV
                TIMEFORMAT AS 'DD/MM/YYYY HH24:MI';
            """)

        elif target_table == "transaction_item":
            cur.execute(f"""
                COPY transaction_item (id, transaction_id, item_id, variant_id, quantity)
                FROM 's3://{bucket_name}/{filename}'
                IAM_ROLE 'arn:aws:iam::{aws_account}:role/RedshiftS3Role'
                CSV;
            """)
        elif target_table == "item":
            cur.execute(f"""
                COPY item (id, name, size, price)
                FROM 's3://{bucket_name}/{filename}'
                IAM_ROLE 'arn:aws:iam::{aws_account}:role/RedshiftS3Role'
                CSV;
            """)
        elif target_table == "variant":
            cur.execute(f"""
                COPY variant (id, name)
                FROM 's3://{bucket_name}/{filename}'
                IAM_ROLE 'arn:aws:iam::{aws_account}:role/RedshiftS3Role'
                CSV;
            """)
        elif target_table == "branch":
            cur.execute(f"""
                COPY branch (id, name)
                FROM 's3://{bucket_name}/{filename}'
                IAM_ROLE 'arn:aws:iam::{aws_account}:role/RedshiftS3Role'
                CSV;
            """)

        logger.debug("Committing changes...")
        conn.commit()
        logger.debug("Done inserting %s, %s, %s",
                        filename, target_table, bucket_name)