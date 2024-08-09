import csv
import io

import boto3
import os
import json

from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import datetime

load_dotenv()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_sqs_queue_url = os.getenv("AWS_SQS_QUEUE_URL")
aws_region = os.getenv("AWS_REGION")
bucket_name = os.getenv("AWS_S3_BUCKET")
s3_filename = f"{datetime.datetime.now()}-report.csv"


def get_batch_size():
    ssm = boto3.client("ssm")
    parameter_name = "BatchSize"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_chunk_size():
    ssm = boto3.client("ssm")
    parameter_name = "ChunkSize"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_listening_duration():
    ssm = boto3.client("ssm")
    parameter_name = "ListeningDurationSec"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_sampling_rate():
    ssm = boto3.client("ssm")
    parameter_name = "SamplingRateHZ"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_sqs_url():
    client = boto3.client("ssm", region_name=aws_region)
    response = client.get_parameter(Name="SonarSQSURL")
    return response["Parameter"]["Value"]


def send_rms_to_sqs(message):
    sqs = boto3.client("sqs", region_name=aws_region)
    queue_url = aws_sqs_queue_url

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
        MessageGroupId="rms_values",
    )
    print(f"Sent RMS values to SQS: {message}")
    return response


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


def upload_file_to_s3(file_name, object_name=None):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    if object_name is None:
        object_name = file_name

    s3.upload_file(file_name, bucket_name, object_name)
    print(f"File {file_name} uploaded to {bucket_name}/{object_name}")
    return True


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
