import csv
import io

import boto3
import os

from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import datetime

load_dotenv()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_sqs_queue_url = os.getenv("AWS_SQS_QUEUE_URL")
bucket_name = os.getenv("AWS_S3_BUCKET")
s3_filename = f"{datetime.datetime.now()}-report.csv"


def create_csv(data: list) -> str:
    """
    Create a CSV file from the given data
    :param data: [
        ['Name', 'Age],
        ['Alice', 24],
        ['Bob', 30],
        ['Charlie', 45],
    ]
    :return: CSV content
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    csv_content = output.getvalue()
    output.close()

    return csv_content


def upload_to_s3(csv_content: str):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3.put_object(Bucket=bucket_name, Key=s3_filename, Body=csv_content)
        print(
            f"CSV content uploaded to S3 bucket '{bucket_name}' with key '{s3_filename}'"
        )
    except NoCredentialsError:
        print("Credentials not available")


def send_message_to_sqs(message_body=None, message_attributes=None):
    sqs_client = boto3.client("sqs")

    if message_attributes is None:
        message_attributes = {}

    # Send the message
    response = sqs_client.send_message(
        QueueUrl=aws_sqs_queue_url,
        MessageBody=message_body,
        MessageAttributes=message_attributes,
    )

    return response
