import boto3
import os

from botocore.exceptions import NoCredentialsError

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = 'your-bucket-name'
s3_filename = 'people.csv'


def upload_to_s3(csv_content):
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        s3.put_object(Bucket=bucket_name, Key=s3_filename, Body=csv_content)
        print(f"CSV content uploaded to S3 bucket '{bucket_name}' with key '{s3_filename}'")
    except NoCredentialsError:
        print("Credentials not available")
